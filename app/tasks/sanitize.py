import re
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PIXELS = 40_000_000
IMAGE_FORMATS = {"image/png": "PNG", "image/jpeg": "JPEG"}
Image.MAX_IMAGE_PIXELS = MAX_PIXELS
PDF_ESCAPED_NAME = re.compile(rb"#([0-9A-Fa-f]{2})")
PDF_ACTIVE_CONTENT = re.compile(rb"/(JavaScript|JS|Launch|EmbeddedFile|RichMedia|XFA)(?![A-Za-z0-9])")


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


def check_pdf(content):
    if b"%%EOF" not in content[-2048:]:
        raise ValueError("Ce PDF est incomplet ou abîmé.")
    names = PDF_ESCAPED_NAME.sub(lambda match: bytes.fromhex(match.group(1).decode()), content)
    if PDF_ACTIVE_CONTENT.search(names):
        raise ValueError("Ce PDF contient du code ou des fichiers cachés. Il a été refusé.")
    return content


def clean_file(content, mime_type):
    if mime_type == "application/pdf":
        return check_pdf(content)
    return clean_image(content, mime_type)
