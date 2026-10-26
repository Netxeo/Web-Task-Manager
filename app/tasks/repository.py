from datetime import datetime

from app.db import get_db
from app.tasks import tags
from app.tasks.filters import SORTS

TASK_COLUMNS = (
    "t.id, t.title, t.description, t.is_done, t.priority, t.due_at, t.created_at, t.updated_at, "
    "(SELECT group_concat(g.name, ',') FROM task_tags tt JOIN tags g ON g.id = tt.tag_id "
    "WHERE tt.task_id = t.id) AS tag_names"
)


def now():
    return datetime.now().isoformat(timespec="seconds")


def to_task(row):
    task = dict(row)
    task["tags"] = sorted(task.pop("tag_names").split(",")) if row["tag_names"] else []
    return task


def escape_like(text):
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def build_where(filters):
    clauses, params = [], []
    if filters["status"] != "all":
        clauses.append("t.is_done = ?")
        params.append(1 if filters["status"] == "done" else 0)
    if filters["q"]:
        pattern = f"%{escape_like(filters['q'])}%"
        clauses.append("(t.title LIKE ? ESCAPE '\\' OR t.description LIKE ? ESCAPE '\\')")
        params += [pattern, pattern]
    if filters["tag"]:
        clauses.append(
            "EXISTS (SELECT 1 FROM task_tags tt JOIN tags g ON g.id = tt.tag_id "
            "WHERE tt.task_id = t.id AND g.name = ?)"
        )
        params.append(filters["tag"])
    if filters["priority"]:
        clauses.append("t.priority = ?")
        params.append(filters["priority"])
    return (" WHERE " + " AND ".join(clauses) if clauses else ""), params


def list_tasks(filters):
    where, params = build_where(filters)
    order = "t.is_done ASC, " + SORTS[filters["sort"]][1]
    rows = get_db().execute(
        f"SELECT {TASK_COLUMNS} FROM tasks t{where} ORDER BY {order}", params
    ).fetchall()
    return [to_task(row) for row in rows]


def get_task(task_id):
    row = get_db().execute(
        f"SELECT {TASK_COLUMNS} FROM tasks t WHERE t.id = ?", (task_id,)
    ).fetchone()
    return to_task(row) if row else None


def count_tasks():
    row = get_db().execute(
        "SELECT COUNT(*) AS total, COALESCE(SUM(is_done), 0) AS done FROM tasks"
    ).fetchone()
    return {"all": row["total"], "done": row["done"], "todo": row["total"] - row["done"]}


def list_tags():
    return tags.list_tags(get_db())


def create_task(data):
    db = get_db()
    timestamp = now()
    with db:
        cursor = db.execute(
            "INSERT INTO tasks (title, description, priority, due_at, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (data["title"], data["description"], data["priority"], data["due_at"], timestamp, timestamp),
        )
        tags.set_task_tags(db, cursor.lastrowid, data["tags"])
    return cursor.lastrowid


def update_task(task_id, data):
    db = get_db()
    with db:
        cursor = db.execute(
            "UPDATE tasks SET title = ?, description = ?, priority = ?, due_at = ?, updated_at = ? "
            "WHERE id = ?",
            (data["title"], data["description"], data["priority"], data["due_at"], now(), task_id),
        )
        if cursor.rowcount:
            tags.set_task_tags(db, task_id, data["tags"])
    return cursor.rowcount == 1


def toggle_task(task_id):
    db = get_db()
    with db:
        cursor = db.execute(
            "UPDATE tasks SET is_done = 1 - is_done, updated_at = ? WHERE id = ?", (now(), task_id)
        )
    return cursor.rowcount == 1


def delete_task(task_id):
    db = get_db()
    with db:
        cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        tags.delete_orphan_tags(db)
    return cursor.rowcount == 1
