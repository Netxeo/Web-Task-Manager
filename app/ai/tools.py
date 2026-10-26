from werkzeug.datastructures import MultiDict

from app.tasks import repository
from app.tasks.filters import PRIORITIES, parse_filters
from app.tasks.forms import TaskForm, form_values

FIELDS = ("title", "description", "priority", "due_at", "tags")


def describe(task):
    return {
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "done": bool(task["is_done"]),
        "priority": PRIORITIES.get(task["priority"], "Aucune"),
        "due_at": task["due_at"],
        "completed_at": task["completed_at"],
        "tags": task["tags"],
    }


def find(task_id):
    task = repository.get_task(int(task_id)) if str(task_id).isdecimal() else None
    if task is None:
        raise ValueError(f"Aucune tâche avec l'identifiant {task_id}.")
    return task


def validated(values):
    form = TaskForm(formdata=MultiDict({key: values[key] for key in FIELDS}), meta={"csrf": False})
    if not form.validate():
        details = "; ".join(f"{name} : {' '.join(errors)}" for name, errors in form.errors.items())
        raise ValueError(f"Données invalides. {details}")
    return form.to_data()


def as_text(values):
    due = values["due_at"]
    return {
        **{key: "" if values[key] is None else str(values[key]) for key in FIELDS},
        "due_at": due.strftime("%Y-%m-%dT%H:%M") if hasattr(due, "strftime") else (due or ""),
    }


def list_tasks(view, query, tag, priority, sort):
    filters = parse_filters({"view": view, "q": query, "tag": tag, "priority": priority, "sort": sort})
    return [describe(task) for task in repository.list_tasks(filters)]


def get_task(task_id):
    return describe(find(task_id))


def create_task(values):
    task_id = repository.create_task(validated(as_text(values)))
    return describe(find(task_id))


def update_task(task_id, changes):
    task = find(task_id)
    values = as_text(form_values(task))
    values.update({key: str(value) for key, value in changes.items() if value is not None})
    repository.update_task(task["id"], validated(values))
    return describe(find(task_id))


def set_done(task_id, done):
    task = find(task_id)
    if bool(task["is_done"]) != done:
        repository.toggle_task(task["id"])
    return describe(find(task_id))


def delete_task(task_id):
    task = find(task_id)
    repository.delete_task(task["id"])
    return {"deleted": task["id"], "title": task["title"]}
