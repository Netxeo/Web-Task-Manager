from flask import abort, redirect, render_template, request, url_for

from app.tasks.data import attachments, details
from app.tasks.data import tasks as task_data
from app.tasks.detail_forms import AttachmentForm, CommentForm, LinkForm, SubtaskForm
from app.tasks.filters import PRIORITIES, STATUSES, VIEWS, has_active_filters, parse_filters, query_args
from app.tasks.moments import shift_week, week_bounds, week_days, week_start

TABS = {"details": "Détails", "subtasks": "Sous-tâches", "comments": "Commentaires", "resources": "Fichiers et liens"}
WRITE_LIMIT = "60 per minute"


def find_task_or_404(task_id):
    task = task_data.get_task(task_id)
    if task is None:
        abort(404)
    return task


def submitted_filters():
    prefix = "filter_"
    return parse_filters({key[len(prefix):]: value for key, value in request.form.items() if key.startswith(prefix)})


def back_to_board(task_id=None, tab=None):
    extra = {"edit": task_id, "tab": tab} if task_id else {}
    return redirect(url_for("tasks.index", **query_args(submitted_filters()), **{k: v for k, v in extra.items() if v}))


def wants_json():
    return request.accept_mimetypes.best == "application/json"


def planner_context(filters):
    monday = week_start(filters["week"])
    dated, backlog = task_data.list_week(filters, *week_bounds(monday))
    days = [(day, [task for task in dated if task["due_at"][:10] == day.isoformat()]) for day in week_days(monday)]
    return {"days": days, "backlog": backlog, "previous_week": shift_week(monday, -1), "next_week": shift_week(monday, 1)}


def detail_context(task, forms):
    defaults = {
        "subtask_form": SubtaskForm(formdata=None),
        "comment_form": CommentForm(formdata=None),
        "link_form": LinkForm(formdata=None),
        "attachment_form": AttachmentForm(formdata=None),
    }
    return {
        **defaults,
        **forms,
        "subtasks": details.list_subtasks(task["id"]),
        "comments": details.list_comments(task["id"]),
        "links": details.list_links(task["id"]),
        "attachments": attachments.list_attachments(task["id"]),
    }


def render_page(filters, panel=None, form=None, editing=None, tab="details", forms=None, status=200):
    context = planner_context(filters) if filters["view"] == "planner" else {
        "columns": task_data.list_board(filters, STATUSES)
    }
    if editing:
        context.update(detail_context(editing, forms or {}))
    page = render_template(
        "tasks/index.html",
        filters=filters,
        filters_active=has_active_filters(filters),
        statuses=STATUSES,
        priorities=PRIORITIES,
        views=VIEWS,
        tabs=TABS,
        tab=tab if tab in TABS else "details",
        tags=task_data.list_tags(),
        total=task_data.count_tasks(),
        panel=panel,
        form=form,
        editing=editing,
        **context,
    )
    return page, status
