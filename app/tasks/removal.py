from app.tasks import uploads
from app.tasks.data import attachments
from app.tasks.data import tasks as task_data


def delete_task_with_files(task_id):
    stored = attachments.stored_names(task_id)
    if not task_data.delete_task(task_id):
        return False
    for name in stored:
        uploads.remove(name)
    return True
