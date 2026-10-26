from flask import request

from app.core.converters import parse_id
from app.tasks import bp
from app.tasks.filters import parse_filters
from app.tasks.forms import TaskForm, form_values
from app.tasks.routes.common import edit_panel, find_task_or_404, new_panel, render_page


@bp.get("/")
def index():
    filters = parse_filters(request.args)
    edit_id = request.args.get("edit", type=parse_id)
    if edit_id is not None:
        task = find_task_or_404(edit_id)
        form = TaskForm(formdata=None, data=form_values(task))
        return render_page(filters, edit_panel(task, form, request.args.get("tab", "")))
    if request.args.get("new") == "1":
        status = request.args.get("status", "new")
        return render_page(filters, new_panel(TaskForm(formdata=None, data={"status": status})))
    return render_page(filters)
