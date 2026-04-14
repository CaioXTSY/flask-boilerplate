from __future__ import annotations

from pathlib import Path

from setup.file_utils import ROOT, inject_before, read_file, write_file
from setup.modules.base import FeatureModule

_API_INIT = """\
from __future__ import annotations

from flask import Blueprint

api_v1_bp = Blueprint("api_v1", __name__)

from app.routes.api.v1 import users  # noqa: E402, F401
"""

_USERS_BLUEPRINT = """\
from __future__ import annotations

from flask import jsonify

from app.routes.api.v1 import api_v1_bp


@api_v1_bp.route("/users", methods=["GET"])
def list_users():
    \"\"\"Return a paginated list of users.

    Replace this stub with real query logic.
    \"\"\"
    return jsonify({"users": [], "total": 0}), 200
"""


class APIModeModule(FeatureModule):
    name = "JSON API Blueprint"
    key = "api_mode"

    def ask(self, state, cli) -> None:
        state.use_api_mode = cli.confirm("Add JSON API blueprint at /api/v1/?", default=False)

    def plan(self, state) -> list[str]:
        if not state.use_api_mode:
            return []
        return [
            "(ADD) app/routes/api/v1/__init__.py  (Blueprint: api_v1_bp)",
            "(ADD) app/routes/api/v1/users.py     (GET /api/v1/users stub)",
            "(ADD) Register api_v1_bp at /api/v1/ in app/__init__.py",
        ]

    def files_touched(self, state) -> list[Path]:
        if not state.use_api_mode:
            return []
        return [ROOT / "app" / "__init__.py"]

    def apply(self, state, rollback) -> None:
        if not state.use_api_mode:
            return

        api_dir = ROOT / "app" / "routes" / "api"
        v1_dir = api_dir / "v1"
        v1_dir.mkdir(parents=True, exist_ok=True)

        api_pkg = api_dir / "__init__.py"
        if not api_pkg.exists():
            write_file(api_pkg, "")
            rollback.register_new_file(api_pkg)

        v1_init = v1_dir / "__init__.py"
        if not v1_init.exists():
            write_file(v1_init, _API_INIT)
            rollback.register_new_file(v1_init)

        users_file = v1_dir / "users.py"
        if not users_file.exists():
            write_file(users_file, _USERS_BLUEPRINT)
            rollback.register_new_file(users_file)

        # Register in app/__init__.py
        init = ROOT / "app" / "__init__.py"
        content = read_file(init)
        if "api_v1_bp" not in content:
            snippet = (
                "\n    from app.routes.api.v1 import api_v1_bp\n"
                "    app.register_blueprint(api_v1_bp, url_prefix=\"/api/v1\")\n"
            )
            content = inject_before(content, "def _register_error_handlers", snippet)
            # Clean up — the injection goes at end of _register_blueprints
            # Better: find the last line of _register_blueprints and inject there
            content = read_file(init)
            lines = content.splitlines(keepends=True)
            result = []
            in_func = False
            for i, line in enumerate(lines):
                result.append(line)
                if "def _register_blueprints" in line:
                    in_func = True
                if in_func and "def _register_error_handlers" in line:
                    # Insert before this line
                    result.pop()
                    result.append("\n")
                    result.append("    from app.routes.api.v1 import api_v1_bp\n")
                    result.append('    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")\n')
                    result.append("\n")
                    result.append(line)
                    in_func = False
            write_file(init, "".join(result))
