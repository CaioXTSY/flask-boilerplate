from __future__ import annotations

import shutil
from pathlib import Path

from setup.file_utils import (
    ROOT,
    env_set,
    read_file,
    remove_lines_containing,
    requirements_remove,
    write_file,
)
from setup.modules.base import FeatureModule


class DatabaseModule(FeatureModule):
    name = "Database"
    key = "database"
    optional = False

    def ask(self, state, cli) -> None:
        backend = cli.choose(
            "Select database backend:",
            options=[
                ("SQLite  (dev only, no server needed)", "sqlite"),
                ("MySQL / MariaDB", "mysql"),
                ("PostgreSQL", "postgresql"),
                ("No database  (disables auth)", "none"),
            ],
            default=1,
        )
        state.db_backend = backend

        if backend in ("mysql", "postgresql"):
            default_port = "3306" if backend == "mysql" else "5432"
            state.db_host = cli.prompt("Host", default="localhost")
            state.db_port = cli.prompt("Port", default=default_port)
            state.db_name = cli.prompt("Database name", default="app")
            state.db_user = cli.prompt("User", default="app")
            state.db_password = cli.prompt("Password", default="", secret=True)

    def plan(self, state) -> list[str]:
        actions = []
        if state.db_backend == "none":
            actions.append("(CONFIGURE) Disable database — remove Flask-SQLAlchemy, Flask-Migrate, migrations/")
            actions.append("(CONFIGURE) Remove db.session.rollback() from error handler")
        elif state.db_backend == "sqlite":
            actions.append("(CONFIGURE) Set DATABASE_URL=sqlite:///instance/dev.db in .env")
            actions.append("(CONFIGURE) Remove MySQL and PostgreSQL drivers from requirements.txt")
        elif state.db_backend == "mysql":
            actions.append(f"(CONFIGURE) Set DATABASE_URL={state.db_url_redacted()} in .env")
            actions.append("(CONFIGURE) Remove psycopg2-binary from requirements.txt")
        elif state.db_backend == "postgresql":
            actions.append(f"(CONFIGURE) Set DATABASE_URL={state.db_url_redacted()} in .env")
            actions.append("(CONFIGURE) Remove PyMySQL and cryptography from requirements.txt")
        return actions

    def files_touched(self, state) -> list[Path]:
        paths = [ROOT / ".env", ROOT / "requirements.txt"]
        if state.db_backend == "none":
            paths += [
                ROOT / "app" / "extensions.py",
                ROOT / "app" / "__init__.py",
                ROOT / "app" / "errors" / "handlers.py",
            ]
        return paths

    def apply(self, state, rollback) -> None:
        req = ROOT / "requirements.txt"

        if state.db_backend == "sqlite":
            env_set(ROOT / ".env", "DATABASE_URL", "sqlite:///instance/dev.db")
            requirements_remove(req, ["PyMySQL", "cryptography", "psycopg2-binary"])

        elif state.db_backend == "mysql":
            env_set(ROOT / ".env", "DATABASE_URL", state.db_url())
            requirements_remove(req, ["psycopg2-binary"])

        elif state.db_backend == "postgresql":
            env_set(ROOT / ".env", "DATABASE_URL", state.db_url())
            requirements_remove(req, ["PyMySQL", "cryptography"])

        elif state.db_backend == "none":
            env_set(ROOT / ".env", "DATABASE_URL", "")
            requirements_remove(
                req,
                ["Flask-SQLAlchemy", "Flask-Migrate", "SQLAlchemy",
                 "PyMySQL", "cryptography", "psycopg2-binary", "email-validator"],
            )
            # Remove db/migrate from extensions.py
            ext = ROOT / "app" / "extensions.py"
            content = read_file(ext)
            content = remove_lines_containing(content, [
                "from flask_sqlalchemy", "from flask_migrate",
                "SQLAlchemy()", "Migrate()",
                "db = ", "migrate = ",
            ])
            write_file(ext, content)

            # Patch app/__init__.py — remove DB-related init and blueprint code
            init = ROOT / "app" / "__init__.py"
            content = read_file(init)
            content = remove_lines_containing(content, [
                "from app.extensions import db",
                "from app.extensions import db, migrate",
                "db.init_app(app)",
                "migrate.init_app(app",
                "from app.models",
                "ctx.update",
            ])
            write_file(init, content)

            # Patch error handler — remove db.session.rollback()
            handlers = ROOT / "app" / "errors" / "handlers.py"
            content = read_file(handlers)
            content = remove_lines_containing(content, [
                "from app.extensions import db",
                "db.session.rollback()",
            ])
            write_file(handlers, content)

            # Remove migrations directory
            migrations_dir = ROOT / "migrations"
            if migrations_dir.exists():
                shutil.rmtree(migrations_dir)
