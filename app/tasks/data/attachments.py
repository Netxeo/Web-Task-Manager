from app.core.db import get_db
from app.tasks.data.tasks import now

MAX_PER_TASK = 5


def list_attachments(task_id):
    return (
        get_db()
        .execute(
            "SELECT id, original_name, mime_type, size, created_at FROM attachments WHERE task_id = ? ORDER BY id",
            (task_id,),
        )
        .fetchall()
    )


def add_attachment(task_id, original_name, stored_name, mime_type, size):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO attachments (task_id, original_name, stored_name, mime_type, size, created_at) "
            "SELECT ?, ?, ?, ?, ?, ? WHERE (SELECT COUNT(*) FROM attachments WHERE task_id = ?) < ?",
            (task_id, original_name, stored_name, mime_type, size, now(), task_id, MAX_PER_TASK),
        )
    return cursor.rowcount == 1


def get_attachment(task_id, attachment_id):
    return (
        get_db()
        .execute(
            "SELECT id, original_name, stored_name, mime_type FROM attachments WHERE id = ? AND task_id = ?",
            (attachment_id, task_id),
        )
        .fetchone()
    )


def delete_attachment(task_id, attachment_id):
    attachment = get_attachment(task_id, attachment_id)
    if attachment is None:
        return None
    db = get_db()
    with db:
        db.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
    return attachment["stored_name"]


def stored_names(task_id):
    rows = get_db().execute("SELECT stored_name FROM attachments WHERE task_id = ?", (task_id,)).fetchall()
    return [row["stored_name"] for row in rows]
