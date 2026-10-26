from flask import abort, flash, redirect, render_template, request, url_for

from app.extensions import limiter
from app.tasks import bp, repository
from app.tasks.filters import PRIORITIES, SORTS, has_active_filters, parse_filters, query_args
from app.tasks.forms import TaskForm, form_values

WRITE_LIMIT = "60 per minute"


def find_task_or_404(task_id):
    task = repository.get_task(task_id)
    if task is None:
        abort(404)
    return task


def render_board(filters, panel=None, form=None, editing=None, status=200):
    page = render_template(
        "tasks/index.html",
        tasks=repository.list_tasks(filters),
        counts=repository.count_tasks(),
        tags=repository.list_tags(),
        filters=filters,
        filters_active=has_active_filters(filters),
        sorts=SORTS,
        priorities=PRIORITIES,
        panel=panel,
        form=form,
        editing=editing,
    )
    return page, status


def submitted_filters():
    prefix = "filter_"
    return parse_filters({key[len(prefix):]: value for key, value in request.form.items() if key.startswith(prefix)})


def back_to_list():
    return redirect(url_for("tasks.index", **query_args(submitted_filters())))


@bp.get("/")
def index():
    filters = parse_filters(request.args)
    edit_id = request.args.get("edit", type=int)
    if edit_id is not None:
        task = find_task_or_404(edit_id)
        return render_board(filters, "edit", TaskForm(formdata=None, data=form_values(task)), task)
    if request.args.get("new") == "1":
        return render_board(filters, "new", TaskForm(formdata=None))
    return render_board(filters)


@bp.post("/tasks")
@limiter.limit(WRITE_LIMIT)
def create():
    form = TaskForm()
    if not form.validate():
        return render_board(submitted_filters(), "new", form, status=422)
    repository.create_task(form.to_data())
    flash("Tâche ajoutée.")
    return back_to_list()


@bp.post("/tasks/<int:task_id>")
@limiter.limit(WRITE_LIMIT)
def update(task_id):
    task = find_task_or_404(task_id)
    form = TaskForm()
    if not form.validate():
        return render_board(submitted_filters(), "edit", form, task, status=422)
    repository.update_task(task_id, form.to_data())
    flash("Tâche enregistrée.")
    return back_to_list()


@bp.post("/tasks/<int:task_id>/toggle")
@limiter.limit(WRITE_LIMIT)
def toggle(task_id):
    if not repository.toggle_task(task_id):
        abort(404)
    return back_to_list()


@bp.post("/tasks/<int:task_id>/delete")
@limiter.limit(WRITE_LIMIT)
def delete(task_id):
    if not repository.delete_task(task_id):
        abort(404)
    flash("Tâche supprimée.")
    return back_to_list()
