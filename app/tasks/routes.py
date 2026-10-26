from flask import render_template

from app.tasks import bp, repository


@bp.get("/")
def index():
    return render_template("tasks/index.html", tasks=repository.list_tasks())
