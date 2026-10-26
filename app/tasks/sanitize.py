from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from app.tasks.pdf_check import check_pdf

MAX_PIXELS = 40_000_000
IMAGE_FORMATS = {"image/png": "PNG", "image/jpeg": "JPEG"}
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


def clean_image(content, mime_type):
    expected = IMAGE_FORMATS[mime_type]
    try:
        with Image.open(BytesIO(content), formats=[expected]) as image:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError("Image trop grande : 40 millions de pixels maximum.")
            image.load()
            picture = ImageOps.exif_transpose(image)
            if expected == "JPEG" and picture.mode not in ("RGB", "L"):
                picture = picture.convert("RGB")
            output = BytesIO()
            picture.save(output, format=expected, quality=90, optimize=True, icc_profile=image.info.get("icc_profile"))
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
        raise ValueError("Cette image est abîmée ou n'est pas une vraie image.") from None
    return output.getvalue()


def clean_file(content, mime_type):
    if mime_type == "application/pdf":
        return check_pdf(content)
    return clean_image(content, mime_type)
