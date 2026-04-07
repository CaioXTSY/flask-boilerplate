from __future__ import annotations

import os

from flask import Flask

from config import BASE_DIR, config


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__, instance_path=str(BASE_DIR / "instance"))
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    _register_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _configure_logging(app)

    if app.config.get("AUTO_CREATE_TABLES"):
        from app.extensions import db as _db

        with app.app_context():
            _db.create_all()

    @app.shell_context_processor
    def make_shell_context():
        from app.extensions import db as _db
        from app.models.user import User

        return {"db": _db, "User": User}

    return app


def _register_extensions(app: Flask) -> None:
    from app.extensions import csrf, db, login_manager, migrate

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)


def _register_blueprints(app: Flask) -> None:
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")


def _register_error_handlers(app: Flask) -> None:
    from app.errors.handlers import errors_bp

    app.register_blueprint(errors_bp)


def _configure_logging(app: Flask) -> None:
    if not app.testing:
        from app.utils.logger import configure_logging

        configure_logging(app)
