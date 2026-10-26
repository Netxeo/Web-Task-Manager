from flask import Blueprint

bp = Blueprint("tasks", __name__)

from app.tasks import formatting
from app.tasks.routes import board, details, files, tasks
