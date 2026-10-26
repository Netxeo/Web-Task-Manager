from datetime import datetime

from app.core.db import get_db
from app.tasks.data import tags

SELECT_TASKS = (
    "SELECT t.id, t.title, t.description, t.status, t.priority, t.due_at, t.completed_at, t.created_at, t.updated_at, "
    "(SELECT group_concat(g.name, ',') FROM task_tags tt JOIN tags g ON g.id = tt.tag_id "
    "WHERE tt.task_id = t.id) AS tag_names, "
    "(SELECT COUNT(*) FROM subtasks s WHERE s.task_id = t.id) AS subtasks_total, "
    "(SELECT COUNT(*) FROM subtasks s WHERE s.task_id = t.id AND s.is_done = 1) AS subtasks_done, "
    "(SELECT COUNT(*) FROM comments c WHERE c.task_id = t.id) AS comments_count, "
    "(SELECT COUNT(*) FROM links l WHERE l.task_id = t.id) + "
    "(SELECT COUNT(*) FROM attachments a WHERE a.task_id = t.id) AS resources_count "
    "FROM tasks t "
    "WHERE (:task_id IS NULL OR t.id = :task_id) "
    "AND (:pattern IS NULL OR t.title LIKE :pattern ESCAPE '\\' OR t.description LIKE :pattern ESCAPE '\\') "
    "AND (:tag IS NULL OR EXISTS (SELECT 1 FROM task_tags tt JOIN tags g ON g.id = tt.tag_id "
    "WHERE tt.task_id = t.id AND g.name = :tag)) "
    "AND (:priority = 0 OR t.priority = :priority) "
    "AND (:start IS NULL OR t.due_at >= :start) "
    "AND (:end IS NULL OR t.due_at < :end) "
    "AND (:backlog = 0 OR (t.due_at IS NULL AND t.status != 'done')) "
    "ORDER BY t.priority DESC, t.due_at IS NULL, t.due_at ASC, t.created_at DESC"
)
NO_FILTERS = {"q": "", "tag": "", "priority": 0}


def now():
    return datetime.now().isoformat(timespec="seconds")


def to_task(row):
    task = dict(row)
    names = task.pop("tag_names")
    task["tags"] = sorted(names.split(",")) if names else []
    task["is_done"] = task["status"] == "done"
    return task


def escape_like(text):
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def select_tasks(filters, task_id=None, start=None, end=None, backlog=False):
    params = {
        "task_id": task_id,
        "pattern": f"%{escape_like(filters['q'])}%" if filters["q"] else None,
        "tag": filters["tag"] or None,
        "priority": filters["priority"] or 0,
        "start": start,
        "end": end,
        "backlog": int(backlog),
    }
    return [to_task(row) for row in get_db().execute(SELECT_TASKS, params).fetchall()]


def list_board(filters, statuses):
    columns = {status: [] for status in statuses}
    for task in select_tasks(filters):
        columns[task["status"]].append(task)
    return columns


def list_week(filters, start, end):
    return select_tasks(filters, start=start, end=end), select_tasks(filters, backlog=True)


def get_task(task_id):
    found = select_tasks(NO_FILTERS, task_id=task_id)
    return found[0] if found else None


def create_task(data):
    db = get_db()
    timestamp = now()
    status = "scheduled" if data["status"] == "new" and data["due_at"] else data["status"]
    with db:
        cursor = db.execute(
            "INSERT INTO tasks (title, description, status, priority, due_at, completed_at, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data["title"],
                data["description"],
                status,
                data["priority"],
                data["due_at"],
                timestamp if status == "done" else None,
                timestamp,
                timestamp,
            ),
        )
        tags.set_task_tags(db, cursor.lastrowid, data["tags"])
    return cursor.lastrowid


def update_task(task_id, data):
    db = get_db()
    timestamp = now()
    with db:
        cursor = db.execute(
            "UPDATE tasks SET title = ?, description = ?, priority = ?, due_at = ?, updated_at = ? WHERE id = ?",
            (data["title"], data["description"], data["priority"], data["due_at"], timestamp, task_id),
        )
        if cursor.rowcount:
            tags.set_task_tags(db, task_id, data["tags"])
    return cursor.rowcount == 1 and set_status(task_id, data["status"])


def set_status(task_id, status):
    db = get_db()
    timestamp = now()
    with db:
        cursor = db.execute(
            "UPDATE tasks SET status = ?, updated_at = ?, "
            "completed_at = CASE WHEN ? = 'done' THEN COALESCE(completed_at, ?) ELSE NULL END WHERE id = ?",
            (status, timestamp, status, timestamp, task_id),
        )
    return cursor.rowcount == 1


def schedule(task_id, day):
    task = get_task(task_id)
    if task is None:
        return False
    if day is None:
        due_at, status = None, "new" if task["status"] == "scheduled" else task["status"]
    else:
        time = task["due_at"][11:] if task["due_at"] else "09:00"
        due_at, status = f"{day}T{time}", "scheduled" if task["status"] == "new" else task["status"]
    db = get_db()
    with db:
        db.execute(
            "UPDATE tasks SET due_at = ?, status = ?, updated_at = ? WHERE id = ?", (due_at, status, now(), task_id)
        )
    return True


def delete_task(task_id):
    db = get_db()
    with db:
        cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        tags.delete_orphan_tags(db)
    return cursor.rowcount == 1


def list_tags():
    return tags.list_tags(get_db())


def count_tasks():
    return get_db().execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
