from PIL import Image, ImageOps
import pytesseract


def extract_text(image_path):
    image = Image.open(image_path)

    image = ImageOps.grayscale(image)

    image = image.point(
        lambda x: 0 if x < 140 else 255,
        mode="1"
    )

    text = pytesseract.image_to_string(
        image,
        lang="eng",
        config="--psm 6"
    )

    return text