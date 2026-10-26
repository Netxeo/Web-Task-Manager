from flask import abort, flash, send_from_directory

from app.core.db import upload_folder
from app.core.extensions import limiter
from app.tasks import bp, uploads
from app.tasks.data import attachments
from app.tasks.detail_forms import AttachmentForm
from app.tasks.forms import TaskForm, form_values
from app.tasks.routes.common import back_to_board, find_task_or_404, render_page, submitted_filters


@bp.post("/tasks/<id:task_id>/attachments")
@limiter.limit("10 per minute")
def upload(task_id):
    task = find_task_or_404(task_id)
    form = AttachmentForm()
    try:
        if not form.validate():
            raise ValueError("La requête a expiré. Recharge la page.")
        name, extension, mime_type, content = uploads.validate(form.file.data)
        stored_name = uploads.save(content, extension)
        if not attachments.add_attachment(task_id, name, stored_name, mime_type, len(content)):
            uploads.remove(stored_name)
            raise ValueError(f"{attachments.MAX_PER_TASK} fichiers maximum par tâche.")
    except ValueError as error:
        form.file.errors = [str(error)]
        edit_form = TaskForm(formdata=None, data=form_values(task))
        return render_page(submitted_filters(), "edit", edit_form, task, "resources", {"attachment_form": form}, 422)
    flash("Fichier ajouté.")
    return back_to_board(task_id, "resources")


@bp.get("/tasks/<id:task_id>/attachments/<id:attachment_id>")
def download(task_id, attachment_id):
    attachment = attachments.get_attachment(task_id, attachment_id)
    if attachment is None:
        abort(404)
    response = send_from_directory(
        upload_folder(),
        attachment["stored_name"],
        mimetype=attachment["mime_type"],
        as_attachment=True,
        download_name=attachment["original_name"],
    )
    response.headers["Content-Security-Policy"] = "sandbox; default-src 'none'"
    response.headers["Cache-Control"] = "private, no-store"
    return response


@bp.post("/tasks/<id:task_id>/attachments/<id:attachment_id>/delete")
@limiter.limit("60 per minute")
def delete_attachment(task_id, attachment_id):
    stored_name = attachments.delete_attachment(task_id, attachment_id)
    if stored_name is None:
        abort(404)
    uploads.remove(stored_name)
    flash("Fichier supprimé.")
    return back_to_board(task_id, "resources")
