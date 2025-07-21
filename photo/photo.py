import logging
from pathlib import Path
from typing import Dict

import imageio.v3 as iio
import numpy as np
import rawpy

from edits.edit import Brightness, Contrast, Edit, EditStack, Scaling, ScalingProps

logger = logging.getLogger("photo")


class Photo:
    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.editstack = EditStack()

        self.__raw = rawpy.imread(str(self.filepath))
        self._preview_rgb = self.__raw.postprocess(
            use_camera_wb=True, no_auto_bright=True, output_bps=8
        )

    def brighten(self, factor: float):
        edit = Brightness(name="brighten", scale_factor=factor)
        self.editstack.add(edit=edit)

    def crop(self, factor: Dict):
        try:
            scaling_props = ScalingProps(**factor)
        except Exception:
            logger.error("Could not create scaling props", "scaling_props", factor)
            return

        edit = Scaling(name="crop", scale_factor=scaling_props)
        self.editstack.add(edit=edit)

    def contrast(self, factor: float):
        edit = Contrast(name="contrast", scale_factor=factor)
        self.editstack.add(edit=edit)

    def process(self, *, fast_preview: bool = False):
        logger.debug("Processing image: fast_preview = %s", fast_preview)
        img = (
            self._preview_rgb.copy()
            if fast_preview
            else self.__raw.postprocess(
                use_camera_wb=True, no_auto_bright=True, output_bps=16
            )
        )
        for edit in self.editstack:
            img = self._apply(img, edit)
        return img

    def export(self, out_path: str | Path, *, ext: str = ".tiff", **kw):
        img = self.process(fast_preview=False)

        # INFO: 16-bit export
        out = img.astype(np.uint16) if img.dtype != np.uint16 else img
        iio.imwrite(str(out_path), out, extension=ext, **kw)

    def _apply(self, img: np.ndarray, edit: Edit) -> np.ndarray:
        logger.debug("Original image dimensions: %s", img.shape)
        if type(edit) is Brightness:
            return np.clip(img * edit.scale_factor, 0, img.max()).astype(img.dtype)

        if type(edit) is Contrast:
            mean = img.mean(axis=(0, 1), keepdims=True)
            return np.clip(
                (img - mean) * edit.scale_factor + mean, 0, img.max()
            ).astype(img.dtype)

        if type(edit) is Scaling:
            img_x, img_y, _ = img.shape

            def _diag(x1, y1, x2, y2):
                return (x2 - x1) ** 2 + (y2 - y1) ** 2

            if _diag(
                *edit.scale_factor.crop_start, *edit.scale_factor.crop_end
            ) > _diag(0, 0, img_x, img_y):
                logger.exception(
                    "Cannot crop to larger dimensions",
                    "image_x",
                    img_x,
                    "image_y",
                    img_y,
                    "edit.crop_start",
                    edit.scale_factor.crop_start,
                    "edit.crop_end",
                    edit.scale_factor.crop_end,
                    stack_info=True,
                )
                raise ValueError("Cannot crop to larger dimensions")

            return img[
                edit.scale_factor.crop_start[1] : edit.scale_factor.crop_end[1],
                edit.scale_factor.crop_start[0] : edit.scale_factor.crop_end[0],
            ]

        logger.error("Unknown edit", "name", edit.name, "property", edit.property)
        raise ValueError(
            f"Unknown edit: name = {edit.name}, property = {edit.property}"
        )
