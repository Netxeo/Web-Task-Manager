import sqlite3

import pytest

from app import create_app
from app.core.db import get_db
from app.core.security import SECURITY_HEADERS


def test_index_shows_empty_state(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Rien à faire pour l&#39;instant." in response.get_data(as_text=True)


def test_unknown_page_returns_404(client):
    assert client.get("/nope").status_code == 404


def test_security_headers_on_every_response(client):
    for path in ("/", "/nope"):
        response = client.get(path)
        for name, value in SECURITY_HEADERS.items():
            assert response.headers[name] == value


def test_app_refuses_weak_secret_key(tmp_path):
    with pytest.raises(RuntimeError):
        create_app({"SECRET_KEY": "short", "DATABASE": str(tmp_path / "x.db")})


def test_schema_rejects_invalid_rows(app):
    with app.app_context():
        connection = get_db()
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO tasks (title, is_done, created_at, updated_at) VALUES (?, ?, ?, ?)",
                ("", 0, "now", "now"),
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO tasks (title, is_done, created_at, updated_at) VALUES (?, ?, ?, ?)",
                ("ok", 2, "now", "now"),
            )
