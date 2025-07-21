from photo.photo import Photo
import matplotlib.pyplot as plt


def preview_image(img, save=False):
    plt.imshow(img)
    plt.title("Numpy image preview")

    if save:
        plt.savefig("data/edits/img_preview.jpg")
    else:
        plt.show()


def main():
    print("Hello from snapweave!")

    filename = "test_D5600_RAW_1"
    print(f"Editing: {filename}")
    photo = Photo(f"data/raw/{filename}.NEF")
    photo.brighten(1.5)
    photo.crop({"crop_start": (0, 0), "crop_end": (6016, 4016)})

    # preview = photo.process(fast_preview=True)
    # preview_image(preview, save=True)

    photo.export(f"data/edits/{filename}_brigten50.tiff")


if __name__ == "__main__":
    main()
