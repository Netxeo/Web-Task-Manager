from datetime import datetime

from app.core.db import get_db
from app.tasks import tags
from app.tasks.filters import SORTS
from app.tasks.moments import day_start

TASK_COLUMNS = (
    "t.id, t.title, t.description, t.is_done, t.priority, t.due_at, t.completed_at, t.created_at, t.updated_at, "
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


def view_clause(view):
    if view == "done":
        return "t.is_done = 1", []
    if view == "today":
        return "t.is_done = 0 AND t.due_at < ?", [day_start(1)]
    if view == "upcoming":
        return "t.is_done = 0 AND t.due_at >= ? AND t.due_at < ?", [day_start(1), day_start(8)]
    return "t.is_done = 0", []


def build_where(filters):
    clause, params = view_clause(filters["view"])
    clauses = [clause]
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
    return " WHERE " + " AND ".join(clauses), params


def list_tasks(filters):
    where, params = build_where(filters)
    order = SORTS[filters["sort"]][1]
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
        "SELECT COUNT(*) AS total, "
        "COALESCE(SUM(is_done = 0 AND due_at < :tomorrow), 0) AS today, "
        "COALESCE(SUM(is_done = 0 AND due_at >= :tomorrow AND due_at < :next_week), 0) AS upcoming, "
        "COALESCE(SUM(is_done = 0), 0) AS todo, "
        "COALESCE(SUM(is_done = 1), 0) AS done, "
        "COALESCE(SUM(is_done = 1 AND completed_at >= :today), 0) AS done_today "
        "FROM tasks",
        {"today": day_start(0), "tomorrow": day_start(1), "next_week": day_start(8)},
    ).fetchone()
    return dict(row)


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
        timestamp = now()
        cursor = db.execute(
            "UPDATE tasks SET is_done = 1 - is_done, "
            "completed_at = CASE WHEN is_done = 0 THEN ? ELSE NULL END, updated_at = ? WHERE id = ?",
            (timestamp, timestamp, task_id),
        )
    return cursor.rowcount == 1


def delete_task(task_id):
    db = get_db()
    with db:
        cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        tags.delete_orphan_tags(db)
    return cursor.rowcount == 1
