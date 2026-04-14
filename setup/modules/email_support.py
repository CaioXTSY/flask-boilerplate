from __future__ import annotations

from pathlib import Path

from setup.file_utils import ROOT, env_set, extensions_add, inject_before, read_file, requirements_add, write_file
from setup.modules.base import FeatureModule

_CONFIG_SNIPPET = """\
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", "1025"))
    MAIL_USE_TLS: bool = os.environ.get("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME: str | None = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@example.com")
"""


class EmailSupportModule(FeatureModule):
    name = "Email Support"
    key = "email_support"

    def ask(self, state, cli) -> None:
        state.use_email = cli.confirm("Add email support (Flask-Mail)?", default=False)
        if state.use_email:
            state.mail_server = cli.prompt("Mail server", default="localhost")
            state.mail_port = cli.prompt_int("Mail port", default=1025, min_val=1, max_val=65535)

    def plan(self, state) -> list[str]:
        if not state.use_email:
            return []
        return [
            "(ADD) Flask-Mail to requirements.txt",
            "(ADD) mail = Mail() to app/extensions.py",
            f"(ADD) MAIL_SERVER={state.mail_server}, MAIL_PORT={state.mail_port} to .env and config.py",
        ]

    def files_touched(self, state) -> list[Path]:
        if not state.use_email:
            return []
        return [
            ROOT / "requirements.txt",
            ROOT / "app" / "extensions.py",
            ROOT / "app" / "__init__.py",
            ROOT / "config.py",
            ROOT / ".env",
        ]

    def apply(self, state, rollback) -> None:
        if not state.use_email:
            return

        requirements_add(ROOT / "requirements.txt", "Flask-Mail>=0.9,<1.0")

        extensions_add(
            ROOT / "app" / "extensions.py",
            "from flask_mail import Mail",
            "mail = Mail()",
        )

        # Inject mail.init_app(app) into _register_extensions
        init = ROOT / "app" / "__init__.py"
        content = read_file(init)
        if "mail.init_app(app)" not in content:
            content = inject_before(content, "login_manager.init_app(app)", "    mail.init_app(app)\n")
            content = content.replace(
                "    mail.init_app(app)\n",
                "    from app.extensions import mail as _mail\n    _mail.init_app(app)\n",
                1,
            )
            write_file(init, content)

        # Add mail config to config.py Config class
        cfg = ROOT / "config.py"
        content = read_file(cfg)
        if "MAIL_SERVER" not in content:
            content = inject_before(content, "    @staticmethod\n    def init_app", _CONFIG_SNIPPET)
            write_file(cfg, content)

        # .env
        env_set(ROOT / ".env", "MAIL_SERVER", state.mail_server)
        env_set(ROOT / ".env", "MAIL_PORT", str(state.mail_port))
        env_set(ROOT / ".env", "MAIL_USE_TLS", "false")
        env_set(ROOT / ".env", "MAIL_USERNAME", "")
        env_set(ROOT / ".env", "MAIL_PASSWORD", "")
