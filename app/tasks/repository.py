from app.db import get_db


def list_tasks():
    return get_db().execute(
        "SELECT id, title, description, is_done, created_at, updated_at "
        "FROM tasks ORDER BY is_done ASC, created_at DESC"
    ).fetchall()
