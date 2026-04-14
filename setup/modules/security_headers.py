from __future__ import annotations

from pathlib import Path

from setup.file_utils import ROOT, extensions_add, inject_before, read_file, requirements_add, write_file
from setup.modules.base import FeatureModule


class SecurityHeadersModule(FeatureModule):
    name = "Security Headers"
    key = "security_headers"

    def ask(self, state, cli) -> None:
        state.use_security_headers = cli.confirm(
            "Add security headers (Flask-Talisman: CSP, HSTS, X-Frame-Options)?",
            default=False,
        )

    def plan(self, state) -> list[str]:
        if not state.use_security_headers:
            return []
        return [
            "(ADD) flask-talisman to requirements.txt",
            "(ADD) talisman.init_app(app) — disabled in dev, enabled in prod",
        ]

    def files_touched(self, state) -> list[Path]:
        if not state.use_security_headers:
            return []
        return [ROOT / "requirements.txt", ROOT / "app" / "extensions.py", ROOT / "app" / "__init__.py"]

    def apply(self, state, rollback) -> None:
        if not state.use_security_headers:
            return

        requirements_add(ROOT / "requirements.txt", "flask-talisman>=1.1,<2.0")

        extensions_add(
            ROOT / "app" / "extensions.py",
            "from flask_talisman import Talisman",
            "talisman = Talisman()",
        )

        init = ROOT / "app" / "__init__.py"
        content = read_file(init)
        if "talisman.init_app" not in content:
            snippet = (
                "\n    from app.extensions import talisman as _talisman\n"
                "    _talisman.init_app(\n"
                "        app,\n"
                "        force_https=app.config.get('SESSION_COOKIE_SECURE', False),\n"
                "        content_security_policy=False,  # configure per-project\n"
                "    )\n"
            )
            content = inject_before(content, "    _register_blueprints(app)", snippet)
            write_file(init, content)
