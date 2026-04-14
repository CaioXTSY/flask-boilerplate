from __future__ import annotations

import shutil
from pathlib import Path

from setup.file_utils import (
    ROOT,
    read_file,
    remove_jinja_block,
    remove_lines_containing,
    requirements_remove,
    write_file,
)
from setup.modules.base import FeatureModule

# Replacement for the auth-dependent block in index.html
_INDEX_STATIC_BUTTONS = """\
    <a href="{{ url_for('main.about') }}" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 text-sm">About</a>
"""


class AuthenticationModule(FeatureModule):
    name = "Authentication"
    key = "authentication"
    requires = ["database"]

    def ask(self, state, cli) -> None:
        if state.db_backend == "none":
            state.use_auth = False
            return
        state.use_auth = cli.confirm("Keep authentication system?", default=True)

    def plan(self, state) -> list[str]:
        if state.use_auth:
            return ["(KEEP) Authentication system (register, login, logout)"]
        return [
            "(REMOVE) app/routes/auth.py, app/forms/auth_forms.py, app/models/user.py",
            "(REMOVE) app/templates/auth/  (login + register templates)",
            "(REMOVE) Auth navigation from base.html and index.html",
            "(REMOVE) Flask-Login, email-validator from requirements.txt",
        ]

    def files_touched(self, state) -> list[Path]:
        if state.use_auth:
            return []
        return [
            ROOT / "app" / "routes" / "auth.py",
            ROOT / "app" / "forms" / "auth_forms.py",
            ROOT / "app" / "models" / "user.py",
            ROOT / "app" / "templates" / "base.html",
            ROOT / "app" / "templates" / "index.html",
            ROOT / "app" / "routes" / "main.py",
            ROOT / "app" / "__init__.py",
            ROOT / "tests" / "conftest.py",
            ROOT / "requirements.txt",
        ]

    def apply(self, state, rollback) -> None:
        if state.use_auth:
            return

        # ── Delete files ──────────────────────────────────────────────────────
        for p in [
            ROOT / "app" / "routes" / "auth.py",
            ROOT / "app" / "forms" / "auth_forms.py",
            ROOT / "app" / "models" / "user.py",
        ]:
            p.unlink(missing_ok=True)

        auth_templates = ROOT / "app" / "templates" / "auth"
        if auth_templates.exists():
            shutil.rmtree(auth_templates)

        # ── base.html — remove {% if config.DB_ENABLED %} auth nav block ─────
        base_html = ROOT / "app" / "templates" / "base.html"
        content = read_file(base_html)
        content = remove_jinja_block(content, "{% if config.DB_ENABLED %}")
        write_file(base_html, content)

        # ── index.html — replace auth conditional with static buttons ─────────
        index_html = ROOT / "app" / "templates" / "index.html"
        content = read_file(index_html)
        content = remove_jinja_block(content, "{% if current_user.is_authenticated %}")
        # Insert the static replacement after the <div class="flex justify-center gap-3">
        content = content.replace(
            '<div class="flex justify-center gap-3">\n',
            f'<div class="flex justify-center gap-3">\n{_INDEX_STATIC_BUTTONS}',
        )
        write_file(index_html, content)

        # ── app/routes/main.py — remove @db_login_required ────────────────────
        main_routes = ROOT / "app" / "routes" / "main.py"
        content = read_file(main_routes)
        content = remove_lines_containing(content, [
            "from app.utils.decorators import db_login_required",
            "@db_login_required",
        ])
        write_file(main_routes, content)

        # ── app/__init__.py — remove auth_bp registration + login_view ────────
        init = ROOT / "app" / "__init__.py"
        content = read_file(init)
        content = remove_lines_containing(content, [
            "from app.routes.auth import auth_bp",
            "app.register_blueprint(auth_bp",
            'login_manager.login_view = "auth.login"',
            "login_manager.login_view = None",
        ])
        write_file(init, content)

        # ── tests/conftest.py — remove User import + auth_client fixture ──────
        conftest = ROOT / "tests" / "conftest.py"
        if conftest.exists():
            content = read_file(conftest)
            content = remove_lines_containing(content, ["from app.models.user import User"])
            # Remove the auth_client fixture function
            lines = content.splitlines(keepends=True)
            result: list[str] = []
            skip = False
            for line in lines:
                if "def auth_client" in line or (
                    result and result[-1].strip() == "@pytest.fixture(scope=\"function\")"
                    and "def auth_client" in line
                ):
                    # Remove the preceding @pytest.fixture decorator too
                    if result and "@pytest.fixture" in result[-1]:
                        result.pop()
                    skip = True
                    continue
                if skip:
                    # Skip until the next top-level definition
                    if line.strip() and not line[0].isspace() and (
                        line.startswith("@") or line.startswith("def ") or line.startswith("class ")
                    ):
                        skip = False
                        result.append(line)
                    continue
                result.append(line)
            write_file(conftest, "".join(result))

        # ── requirements.txt ──────────────────────────────────────────────────
        requirements_remove(
            ROOT / "requirements.txt",
            ["Flask-Login", "email-validator"],
        )
