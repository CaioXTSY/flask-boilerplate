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
    _register_middleware(app)

    if app.config.get("DB_ENABLED") and app.config.get("AUTO_CREATE_TABLES"):
        from app.extensions import db as _db

        with app.app_context():
            _db.create_all()

    @app.shell_context_processor
    def make_shell_context():
        ctx: dict = {}
        if app.config.get("DB_ENABLED"):
            from app.extensions import db as _db
            from app.models.user import User

            ctx.update({"db": _db, "User": User})
        return ctx

    return app


def _register_extensions(app: Flask) -> None:
    from app.extensions import csrf, login_manager

    csrf.init_app(app)
    login_manager.init_app(app)

    if app.config.get("DB_ENABLED"):
        from app.extensions import db, migrate

        db.init_app(app)
        migrate.init_app(app, db)

        login_manager.login_view = "auth.login"
    else:
        login_manager.login_view = None


def _register_blueprints(app: Flask) -> None:
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)

    if app.config.get("DB_ENABLED"):
        from app.routes.auth import auth_bp

        app.register_blueprint(auth_bp, url_prefix="/auth")


def _register_error_handlers(app: Flask) -> None:
    from app.errors.handlers import errors_bp

    app.register_blueprint(errors_bp)


def _configure_logging(app: Flask) -> None:
    if not app.testing:
        from app.utils.logger import configure_logging

        configure_logging(app)


def _register_middleware(app: Flask) -> None:
    from app.utils.middleware import register_middleware

    register_middleware(app)
