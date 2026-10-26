import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def database_path():
    configured = current_app.config["DATABASE"]
    return configured or str(Path(current_app.instance_path) / "tasks.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(database_path())
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    connection = get_db()
    connection.execute("PRAGMA journal_mode = WAL")
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    connection.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
