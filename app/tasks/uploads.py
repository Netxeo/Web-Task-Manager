import re
import secrets

from app.core.db import upload_folder
from app.tasks.forms import clean_text
from app.tasks.sanitize import clean_file

MAX_SIZE = 5 * 1024 * 1024
SIGNATURES = {
    ".pdf": (b"%PDF-", "application/pdf"),
    ".png": (b"\x89PNG\r\n\x1a\n", "image/png"),
    ".jpg": (b"\xff\xd8\xff", "image/jpeg"),
    ".jpeg": (b"\xff\xd8\xff", "image/jpeg"),
}
UNSAFE_NAME_CHARACTERS = re.compile(r"[\x00-\x1f\x7f/\\:*?\"<>|]")


def clean_name(filename):
    name = " ".join(UNSAFE_NAME_CHARACTERS.sub("", clean_text(filename)).split()).strip(". ")
    return name[-120:] or "fichier"


def validate(file_storage):
    if file_storage is None or not file_storage.filename:
        raise ValueError("Choisis un fichier.")
    name = clean_name(file_storage.filename)
    extension = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if extension not in SIGNATURES:
        raise ValueError("Formats acceptés : PDF, PNG et JPG.")
    content = file_storage.stream.read(MAX_SIZE + 1)
    if not content:
        raise ValueError("Le fichier est vide.")
    if len(content) > MAX_SIZE:
        raise ValueError("5 Mo maximum par fichier.")
    signature, mime_type = SIGNATURES[extension]
    if not content.startswith(signature):
        raise ValueError("Le contenu du fichier ne correspond pas à son extension.")
    content = clean_file(content, mime_type)
    if len(content) > MAX_SIZE:
        raise ValueError("5 Mo maximum par fichier.")
    return name, extension.replace(".jpeg", ".jpg"), mime_type, content


def save(content, extension):
    stored_name = secrets.token_hex(16) + extension
    (upload_folder() / stored_name).write_bytes(content)
    return stored_name


def remove(stored_name):
    (upload_folder() / stored_name).unlink(missing_ok=True)
