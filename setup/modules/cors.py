from __future__ import annotations

from pathlib import Path

from setup.file_utils import ROOT, env_set, extensions_add, inject_before, read_file, requirements_add, write_file
from setup.modules.base import FeatureModule


class CORSModule(FeatureModule):
    name = "CORS"
    key = "cors"

    def ask(self, state, cli) -> None:
        state.use_cors = cli.confirm("Add CORS support (Flask-CORS)?", default=False)
        if state.use_cors:
            state.cors_origins = cli.prompt(
                "Allowed origins (comma-separated, or * for all)",
                default="*",
            )

    def plan(self, state) -> list[str]:
        if not state.use_cors:
            return []
        return [
            "(ADD) Flask-CORS to requirements.txt",
            f"(ADD) CORS_ORIGINS={state.cors_origins} to .env and config.py",
            "(ADD) cors.init_app(app) in _register_extensions",
        ]

    def files_touched(self, state) -> list[Path]:
        if not state.use_cors:
            return []
        return [
            ROOT / "requirements.txt",
            ROOT / "app" / "extensions.py",
            ROOT / "app" / "__init__.py",
            ROOT / "config.py",
            ROOT / ".env",
        ]

    def apply(self, state, rollback) -> None:
        if not state.use_cors:
            return

        requirements_add(ROOT / "requirements.txt", "Flask-Cors>=4.0,<5.0")

        extensions_add(
            ROOT / "app" / "extensions.py",
            "from flask_cors import CORS",
            "cors = CORS()",
        )

        init = ROOT / "app" / "__init__.py"
        content = read_file(init)
        if "cors.init_app" not in content:
            snippet = (
                "\n    from app.extensions import cors as _cors\n"
                "    _cors.init_app(app, origins=app.config.get('CORS_ORIGINS', '*'))\n"
            )
            content = inject_before(content, "    _register_blueprints(app)", snippet)
            write_file(init, content)

        cfg = ROOT / "config.py"
        content = read_file(cfg)
        if "CORS_ORIGINS" not in content:
            cors_line = '    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")\n'
            content = inject_before(content, "    @staticmethod\n    def init_app", cors_line)
            write_file(cfg, content)

        env_set(ROOT / ".env", "CORS_ORIGINS", state.cors_origins)
