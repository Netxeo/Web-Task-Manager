from app.core.db import get_db
from app.tasks.data.tasks import now

LIMITS = {"subtasks": 20, "comments": 200, "links": 10}
DELETE_QUERIES = {
    "subtasks": "DELETE FROM subtasks WHERE id = ? AND task_id = ?",
    "comments": "DELETE FROM comments WHERE id = ? AND task_id = ?",
    "links": "DELETE FROM links WHERE id = ? AND task_id = ?",
}


def write(query, params):
    db = get_db()
    with db:
        cursor = db.execute(query, params)
    return cursor.rowcount == 1


def delete(kind, task_id, item_id):
    return write(DELETE_QUERIES[kind], (item_id, task_id))


def list_subtasks(task_id):
    return get_db().execute(
        "SELECT id, title, is_done FROM subtasks WHERE task_id = ? ORDER BY id", (task_id,)
    ).fetchall()


def add_subtask(task_id, title):
    return write(
        "INSERT INTO subtasks (task_id, title) SELECT ?, ? "
        "WHERE (SELECT COUNT(*) FROM subtasks WHERE task_id = ?) < ?",
        (task_id, title, task_id, LIMITS["subtasks"]),
    )


def toggle_subtask(task_id, subtask_id):
    return write("UPDATE subtasks SET is_done = 1 - is_done WHERE id = ? AND task_id = ?", (subtask_id, task_id))


def list_comments(task_id):
    return get_db().execute(
        "SELECT id, body, created_at FROM comments WHERE task_id = ? ORDER BY id DESC", (task_id,)
    ).fetchall()


def add_comment(task_id, body):
    return write(
        "INSERT INTO comments (task_id, body, created_at) SELECT ?, ?, ? "
        "WHERE (SELECT COUNT(*) FROM comments WHERE task_id = ?) < ?",
        (task_id, body, now(), task_id, LIMITS["comments"]),
    )


def list_links(task_id):
    return get_db().execute("SELECT id, url, label FROM links WHERE task_id = ? ORDER BY id", (task_id,)).fetchall()


def add_link(task_id, url, label):
    return write(
        "INSERT INTO links (task_id, url, label) SELECT ?, ?, ? "
        "WHERE (SELECT COUNT(*) FROM links WHERE task_id = ?) < ?",
        (task_id, url, label, task_id, LIMITS["links"]),
    )
