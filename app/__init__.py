from pathlib import Path

from flask import Flask

from app import db, errors, security
from app.config import Config
from app.extensions import csrf, limiter
from app.tasks import bp as tasks_bp


def create_app(overrides=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)
    Config.validate(app.config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    csrf.init_app(app)
    limiter.init_app(app)
    db.init_app(app)
    security.init_app(app)
    errors.init_app(app)
    app.register_blueprint(tasks_bp)

    return app
