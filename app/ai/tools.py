from werkzeug.datastructures import MultiDict

from app.tasks.data import details
from app.tasks.data import tasks as task_data
from app.tasks.detail_forms import CommentForm, SubtaskForm
from app.tasks.filters import PRIORITIES, STATUSES, parse_filters
from app.tasks.forms import TaskForm, form_values
from app.tasks.removal import delete_task_with_files

FIELDS = ("title", "description", "status", "priority", "due_at", "tags")


def describe(task):
    return {
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "column": STATUSES[task["status"]],
        "priority": PRIORITIES.get(task["priority"], "Aucune"),
        "due_at": task["due_at"],
        "tags": task["tags"],
        "subtasks": f"{task['subtasks_done']}/{task['subtasks_total']}",
        "comments": task["comments_count"],
    }


def find(task_id):
    task = task_data.get_task(int(task_id)) if str(task_id).isdecimal() else None
    if task is None:
        raise ValueError(f"Aucune tâche avec l'identifiant {task_id}.")
    return task


def validated(form_class, values):
    form = form_class(formdata=MultiDict(values), meta={"csrf": False})
    if not form.validate():
        problems = "; ".join(f"{name} : {' '.join(errors)}" for name, errors in form.errors.items())
        raise ValueError(f"Données invalides. {problems}")
    return form


def as_text(values):
    due = values["due_at"]
    return {
        **{key: "" if values[key] is None else str(values[key]) for key in FIELDS},
        "due_at": due.strftime("%Y-%m-%dT%H:%M") if hasattr(due, "strftime") else (due or ""),
    }


def list_tasks(status, query, tag, priority):
    filters = parse_filters({"q": query, "tag": tag, "priority": priority})
    columns = task_data.list_board(filters, STATUSES)
    chosen = [status] if status in STATUSES else list(STATUSES)
    return [describe(task) for key in chosen for task in columns[key]]


def get_task(task_id):
    task = find(task_id)
    return {
        **describe(task),
        "subtask_items": [dict(item) for item in details.list_subtasks(task["id"])],
        "comment_items": [dict(item) for item in details.list_comments(task["id"])],
        "links": [dict(item) for item in details.list_links(task["id"])],
    }


def create_task(values):
    form = validated(TaskForm, as_text(values))
    return describe(find(task_data.create_task(form.to_data())))


def update_task(task_id, changes):
    task = find(task_id)
    values = as_text(form_values(task))
    values.update({key: str(value) for key, value in changes.items() if value is not None})
    task_data.update_task(task["id"], validated(TaskForm, values).to_data())
    return describe(find(task_id))


def move_task(task_id, status):
    if status not in STATUSES:
        raise ValueError(f"Colonne inconnue. Choix possibles : {', '.join(STATUSES)}.")
    task_data.set_status(find(task_id)["id"], status)
    return describe(find(task_id))


def add_subtask(task_id, title):
    task = find(task_id)
    if not details.add_subtask(task["id"], validated(SubtaskForm, {"title": title}).title.data):
        raise ValueError("Limite de sous-tâches atteinte.")
    return get_task(task_id)


def add_comment(task_id, body):
    task = find(task_id)
    if not details.add_comment(task["id"], validated(CommentForm, {"body": body}).body.data):
        raise ValueError("Limite de commentaires atteinte.")
    return get_task(task_id)


def delete_task(task_id):
    task = find(task_id)
    delete_task_with_files(task["id"])
    return {"deleted": task["id"], "title": task["title"]}
