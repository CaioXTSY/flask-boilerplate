from __future__ import annotations

from pathlib import Path

from setup.file_utils import ROOT, extensions_add, inject_after, read_file, requirements_add, write_file
from setup.modules.base import FeatureModule


class RateLimitingModule(FeatureModule):
    name = "Rate Limiting"
    key = "rate_limiting"
    requires = ["authentication"]

    def ask(self, state, cli) -> None:
        if not state.use_auth:
            state.use_rate_limiting = False
            return
        state.use_rate_limiting = cli.confirm("Add rate limiting on auth routes (Flask-Limiter)?", default=False)

    def plan(self, state) -> list[str]:
        if not state.use_rate_limiting:
            return []
        return [
            "(ADD) Flask-Limiter to requirements.txt",
            "(ADD) limiter = Limiter() to app/extensions.py",
            "(ADD) @limiter.limit(\"10 per minute\") on /auth/login and /auth/register",
        ]

    def files_touched(self, state) -> list[Path]:
        if not state.use_rate_limiting:
            return []
        return [
            ROOT / "requirements.txt",
            ROOT / "app" / "extensions.py",
            ROOT / "app" / "__init__.py",
            ROOT / "app" / "routes" / "auth.py",
        ]

    def apply(self, state, rollback) -> None:
        if not state.use_rate_limiting:
            return

        requirements_add(ROOT / "requirements.txt", "Flask-Limiter>=3.5,<4.0")

        extensions_add(
            ROOT / "app" / "extensions.py",
            "from flask_limiter import Limiter\nfrom flask_limiter.util import get_remote_address",
            "limiter = Limiter(key_func=get_remote_address, default_limits=[])",
        )

        # Inject limiter.init_app(app)
        init = ROOT / "app" / "__init__.py"
        content = read_file(init)
        if "limiter.init_app(app)" not in content:
            content = inject_after(
                content,
                "csrf.init_app(app)",
                "\n    from app.extensions import limiter as _limiter\n    _limiter.init_app(app)\n",
            )
            write_file(init, content)

        # Add decorators to auth routes
        auth = ROOT / "app" / "routes" / "auth.py"
        content = read_file(auth)
        if "limiter" not in content:
            # Add import
            content = content.replace(
                "from app.extensions import db\n",
                "from app.extensions import db, limiter\n",
            )
            # Add decorator before register route
            content = content.replace(
                '@auth_bp.route("/register"',
                '@limiter.limit("10 per minute")\n@auth_bp.route("/register"',
            )
            # Add decorator before login route
            content = content.replace(
                '@auth_bp.route("/login"',
                '@limiter.limit("10 per minute")\n@auth_bp.route("/login"',
            )
            write_file(auth, content)
