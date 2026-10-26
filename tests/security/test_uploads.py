import io
import os
import zlib
from pathlib import Path

import pytest
from PIL import Image

from app.tasks.data import attachments

PDF = b"%PDF-1.4\n%test\n%%EOF\n"


def picture(image_format, exif=None):
    output = io.BytesIO()
    Image.new("RGB", (4, 2), "orange").save(output, format=image_format, **({"exif": exif} if exif else {}))
    return output.getvalue()


PNG = picture("PNG")


def object_stream_pdf(inner, filters=b"/FlateDecode", data=None):
    data = zlib.compress(inner) if data is None else data
    head = b"%PDF-1.7\n1 0 obj\n<< /Type /ObjStm /N 1 /First 4 /Filter " + filters + b" >>\nstream\n"
    return head + data + b"\nendstream\nendobj\n%%EOF\n"


def send(client, content, name, task_id=1):
    return client.post(
        f"/tasks/{task_id}/attachments",
        data={"file": (io.BytesIO(content), name)},
        content_type="multipart/form-data",
    )


@pytest.fixture
def task(add_task):
    add_task("Avec fichiers")
    add_task("Autre tâche")
    return 1


def stored_files(app):
    return list(Path(app.config["UPLOAD_FOLDER"]).glob("*"))


def test_valid_files_are_stored_under_random_names(app, client, task):
    assert send(client, PDF, "facture été.pdf").status_code == 302
    assert send(client, PNG, "capture.png").status_code == 302
    with app.app_context():
        names = [row["original_name"] for row in attachments.list_attachments(1)]
    assert names == ["facture été.pdf", "capture.png"]
    assert all(len(path.stem) == 32 for path in stored_files(app))


@pytest.mark.parametrize(
    "content, name, message",
    [
        (b"<html><script>alert(1)</script>", "piege.pdf", "ne correspond pas"),
        (b"<svg onload=alert(1)>", "image.svg", "Formats acceptés"),
        (PDF, "script.html", "Formats acceptés"),
        (PDF, "sans_extension", "Formats acceptés"),
        (b"", "vide.pdf", "vide"),
        (b"\x89PNG\r\n\x1a\n<script>alert(1)</script>", "faux.png", "pas une vraie image"),
        (b"\xff\xd8\xff<?php system($_GET[0]); ?>", "faux.jpg", "pas une vraie image"),
        (b"%PDF-1.4\n<< /OpenAction << /S /JavaScript /JS (app.alert(1)) >> >>\n%%EOF", "script.pdf", "code ou des fichiers"),
        (b"%PDF-1.4\n<< /S /J#61vaScript >>\n%%EOF", "cache.pdf", "code ou des fichiers"),
        (b"%PDF-1.4\n<< /Type /Launch /F (calc.exe) >>\n%%EOF", "lance.pdf", "code ou des fichiers"),
        (b"%PDF-1.4\nsans fin", "coupe.pdf", "incomplet"),
    ],
)
def test_dangerous_or_invalid_files_are_refused(app, client, task, content, name, message):
    response = send(client, content, name)
    assert response.status_code == 422
    assert message in response.get_data(as_text=True)
    assert stored_files(app) == []


def test_file_size_is_limited(app, client, task):
    response = send(client, PDF + b"0" * (5 * 1024 * 1024), "lourd.pdf")
    assert response.status_code in (413, 422)
    assert stored_files(app) == []


def test_large_real_files_are_accepted(app, client, task):
    photo = io.BytesIO()
    Image.frombytes("RGB", (1200, 900), os.urandom(1200 * 900 * 3)).save(photo, format="JPEG", quality=95)
    assert len(photo.getvalue()) > 1024 * 1024
    assert send(client, photo.getvalue(), "photo.jpg").status_code == 302
    assert send(client, PDF.replace(b"%test", b"%" + b"x" * 3 * 1024 * 1024), "gros.pdf").status_code == 302
    assert len(stored_files(app)) == 2


def test_real_and_compressed_pdfs_are_accepted(app, client, task):
    output = io.BytesIO()
    Image.new("RGB", (20, 20), "white").save(output, format="PDF")
    assert send(client, output.getvalue(), "scan.pdf").status_code == 302
    assert send(client, object_stream_pdf(b"2 0 << /Type /Page >>"), "compresse.pdf").status_code == 302


@pytest.mark.parametrize(
    "content, message",
    [
        (object_stream_pdf(b"2 0 << /S /JavaScript /JS (app.alert(1)) >>"), "code ou des fichiers"),
        (object_stream_pdf(b"2 0 << /Type /EmbeddedFile >>"), "code ou des fichiers"),
        (object_stream_pdf(b"2 0 << /S /J#61vaScript >>"), "code ou des fichiers"),
        (object_stream_pdf(b"", b"/LZWDecode", b"donnees"), "empêche de le vérifier"),
        (object_stream_pdf(b"", data=zlib.compress(b"0" * 30 * 1024 * 1024)), "empêche de le vérifier"),
        (object_stream_pdf(b"", data=b"pas du zlib"), "empêche de le vérifier"),
        (b"%PDF-1.7\n<< /Encrypt 5 0 R >>\n%%EOF", "empêche de le vérifier"),
    ],
    ids=["javascript", "fichier-cache", "nom-camoufle", "compression-inconnue", "bombe", "flux-casse", "chiffre"],
)
def test_pdf_content_hidden_in_compressed_streams_is_found(app, client, task, content, message):
    response = send(client, content, "cache.pdf")
    assert response.status_code == 422
    assert message in response.get_data(as_text=True)
    assert stored_files(app) == []


def test_image_metadata_is_removed_and_orientation_kept(app, client, task):
    exif = Image.Exif()
    exif[0x0112] = 6
    exif[0x010F] = "Appareil secret"
    exif[0x8825] = {2: (46.0, 30.0, 0.0)}
    send(client, picture("JPEG", exif), "photo.jpg")
    stored = stored_files(app)[0].read_bytes()
    assert b"Appareil secret" not in stored and b"Exif" not in stored
    with Image.open(io.BytesIO(stored)) as image:
        assert image.size == (2, 4)


def test_hidden_characters_are_removed_from_file_names(app, client, task):
    send(client, PDF, "facture\u202efdp.exe.pdf")
    with app.app_context():
        assert attachments.list_attachments(1)[0]["original_name"] == "facturefdp.exe.pdf"


def test_file_name_cannot_escape_the_folder(app, client, task):
    send(client, PDF, "../../etc/passwd.pdf")
    with app.app_context():
        assert attachments.list_attachments(1)[0]["original_name"] == "etcpasswd.pdf"
    assert all(path.parent == Path(app.config["UPLOAD_FOLDER"]) for path in stored_files(app))


def test_download_is_forced_and_sandboxed(client, task):
    send(client, PDF, "rapport.pdf")
    response = client.get("/tasks/1/attachments/1")
    assert response.status_code == 200
    assert response.data == PDF
    assert response.headers["Content-Disposition"].startswith("attachment")
    assert response.headers["Content-Security-Policy"] == "sandbox; default-src 'none'"
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_files_are_scoped_to_their_task(client, task):
    send(client, PDF, "rapport.pdf")
    assert client.get("/tasks/2/attachments/1").status_code == 404
    assert client.post("/tasks/2/attachments/1/delete").status_code == 404


def test_attachment_limit(app, client, task):
    for number in range(6):
        send(client, PDF, f"fichier{number}.pdf")
    with app.app_context():
        assert len(attachments.list_attachments(1)) == attachments.MAX_PER_TASK


def test_deleting_removes_files_from_disk(app, client, task):
    send(client, PDF, "a.pdf")
    send(client, PDF, "b.pdf")
    client.post("/tasks/1/attachments/1/delete")
    assert len(stored_files(app)) == 1
    client.post("/tasks/1/delete")
    assert stored_files(app) == []
