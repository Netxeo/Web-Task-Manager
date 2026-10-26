from flask import abort, flash

from app.core.extensions import limiter
from app.tasks import bp
from app.tasks.data import details
from app.tasks.detail_forms import CommentForm, LinkForm, SubtaskForm
from app.tasks.forms import TaskForm, form_values
from app.tasks.routes.common import (
    WRITE_LIMIT,
    back_to_board,
    edit_panel,
    find_task_or_404,
    render_page,
    submitted_filters,
)

TAB_OF = {"subtasks": "subtasks", "comments": "comments", "links": "resources"}


def refuse(task, tab, form_name, form):
    edit_form = TaskForm(formdata=None, data=form_values(task))
    return render_page(submitted_filters(), edit_panel(task, edit_form, tab, {form_name: form}), 422)


def saved(task_id, tab, added, message):
    flash(message if added else "Limite atteinte pour cette tâche.")
    return back_to_board(task_id, tab)


@bp.post("/tasks/<id:task_id>/subtasks")
@limiter.limit(WRITE_LIMIT)
def add_subtask(task_id):
    task = find_task_or_404(task_id)
    form = SubtaskForm()
    if not form.validate():
        return refuse(task, "subtasks", "subtask_form", form)
    return saved(task_id, "subtasks", details.add_subtask(task_id, form.title.data), "Sous-tâche ajoutée.")


@bp.post("/tasks/<id:task_id>/subtasks/<id:subtask_id>/toggle")
@limiter.limit(WRITE_LIMIT)
def toggle_subtask(task_id, subtask_id):
    if not details.toggle_subtask(task_id, subtask_id):
        abort(404)
    return back_to_board(task_id, "subtasks")


@bp.post("/tasks/<id:task_id>/comments")
@limiter.limit(WRITE_LIMIT)
def add_comment(task_id):
    task = find_task_or_404(task_id)
    form = CommentForm()
    if not form.validate():
        return refuse(task, "comments", "comment_form", form)
    return saved(task_id, "comments", details.add_comment(task_id, form.body.data), "Commentaire ajouté.")


@bp.post("/tasks/<id:task_id>/links")
@limiter.limit(WRITE_LIMIT)
def add_link(task_id):
    task = find_task_or_404(task_id)
    form = LinkForm()
    if not form.validate():
        return refuse(task, "resources", "link_form", form)
    added = details.add_link(task_id, form.url.data, form.label.data or "")
    return saved(task_id, "resources", added, "Lien ajouté.")


@bp.post("/tasks/<id:task_id>/<any(subtasks, comments, links):kind>/<id:item_id>/delete")
@limiter.limit(WRITE_LIMIT)
def delete_detail(task_id, kind, item_id):
    if not details.delete(kind, task_id, item_id):
        abort(404)
    return back_to_board(task_id, TAB_OF[kind])
