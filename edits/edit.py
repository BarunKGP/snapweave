from typing import Dict, Tuple
from pydantic import BaseModel, field_validator


# NOTE: find a way to add validation for available properties:
#
# brightness: float = 1.0
# contrast: float = 1.0
# intensity: float = 1.0
# scale: float = 1.0


class Edit(BaseModel):
    name: str
    property: str


class Brightness(Edit, BaseModel):
    name: str
    scale_factor: float
    property: str = "brightness"


class Contrast(Edit, BaseModel):
    name: str
    scale_factor: float
    property: str = "contrast"


class ScalingProps(BaseModel):
    # INFO: left diagonal corner where crop starts
    crop_start: Tuple[int, int]
    # INFO: right diagonal corner where crop ends
    crop_end: Tuple[int, int]


class Scaling(Edit, BaseModel):
    name: str
    scale_factor: ScalingProps
    property: str = "scaling"


# ----
class EditStack:
    def __init__(self):
        self.edits: list[Edit] = []

    def add(self, edit: Edit):
        self.edits.append(edit)

    def pop(self):
        self.edits.pop()

    def clear(self):
        self.edits.clear()

    def __iter__(self):
        return iter(self.edits)
