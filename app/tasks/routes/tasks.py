from datetime import date

from flask import abort, flash, request

from app.core.extensions import limiter
from app.tasks import bp
from app.tasks.data import tasks as task_data
from app.tasks.filters import STATUSES
from app.tasks.forms import TaskForm
from app.tasks.removal import delete_task_with_files
from app.tasks.routes.common import (
    WRITE_LIMIT,
    back_to_board,
    edit_panel,
    find_task_or_404,
    new_panel,
    render_page,
    submitted_filters,
    wants_json,
)


@bp.post("/tasks")
@limiter.limit(WRITE_LIMIT)
def create():
    form = TaskForm()
    if not form.validate():
        return render_page(submitted_filters(), new_panel(form), 422)
    task_data.create_task(form.to_data())
    flash("Tâche ajoutée.")
    return back_to_board()


@bp.post("/tasks/<id:task_id>")
@limiter.limit(WRITE_LIMIT)
def update(task_id):
    task = find_task_or_404(task_id)
    form = TaskForm()
    if not form.validate():
        return render_page(submitted_filters(), edit_panel(task, form), 422)
    task_data.update_task(task_id, form.to_data())
    flash("Tâche enregistrée.")
    return back_to_board(task_id)


def moved():
    if wants_json():
        return "", 204
    return back_to_board()


@bp.post("/tasks/<id:task_id>/status")
@limiter.limit(WRITE_LIMIT)
def move(task_id):
    status = request.form.get("status", "")
    if status not in STATUSES:
        abort(400)
    if not task_data.set_status(task_id, status):
        abort(404)
    return moved()


@bp.post("/tasks/<id:task_id>/schedule")
@limiter.limit(WRITE_LIMIT)
def schedule(task_id):
    value = request.form.get("day", "")
    try:
        day = date.fromisoformat(value).isoformat() if value else None
    except ValueError:
        abort(400)
    if not task_data.schedule(task_id, day):
        abort(404)
    return moved()


@bp.post("/tasks/<id:task_id>/toggle")
@limiter.limit(WRITE_LIMIT)
def toggle(task_id):
    task = find_task_or_404(task_id)
    reopened = "scheduled" if task["due_at"] else "new"
    task_data.set_status(task_id, reopened if task["is_done"] else "done")
    flash("Tâche rouverte." if task["is_done"] else "Tâche terminée.")
    return back_to_board()


@bp.post("/tasks/<id:task_id>/delete")
@limiter.limit(WRITE_LIMIT)
def delete(task_id):
    if not delete_task_with_files(task_id):
        abort(404)
    flash("Tâche supprimée.")
    return back_to_board()
