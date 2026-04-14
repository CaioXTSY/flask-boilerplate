from __future__ import annotations

from pathlib import Path

from setup.file_utils import ROOT, extensions_add, init_add_to_register_extensions, read_file, requirements_add, write_file
from setup.modules.base import FeatureModule

_ADMIN_INIT = '''\
from __future__ import annotations

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app.extensions import db
from app.models.user import User


class UserModelView(ModelView):
    column_exclude_list = ["password_hash"]
    can_create = False
    can_delete = False


def init_admin(app, admin_instance):
    admin_instance.init_app(app)
    with app.app_context():
        admin_instance.add_view(UserModelView(User, db.session))
'''


class AdminPanelModule(FeatureModule):
    name = "Admin Panel"
    key = "admin_panel"
    requires = ["authentication"]

    def ask(self, state, cli) -> None:
        if not state.use_auth:
            state.use_admin = False
            return
        state.use_admin = cli.confirm("Add Flask-Admin panel?", default=False)

    def plan(self, state) -> list[str]:
        if not state.use_admin:
            return []
        return [
            "(ADD) Flask-Admin to requirements.txt",
            "(ADD) app/admin/__init__.py with User model view",
            "(ADD) admin.init_app(app) in _register_extensions",
        ]

    def files_touched(self, state) -> list[Path]:
        if not state.use_admin:
            return []
        return [ROOT / "requirements.txt", ROOT / "app" / "extensions.py", ROOT / "app" / "__init__.py"]

    def apply(self, state, rollback) -> None:
        if not state.use_admin:
            return

        requirements_add(ROOT / "requirements.txt", "Flask-Admin>=1.6,<2.0")

        extensions_add(
            ROOT / "app" / "extensions.py",
            "from flask_admin import Admin",
            "admin = Admin(name=None, template_mode='bootstrap4')",
        )

        admin_dir = ROOT / "app" / "admin"
        admin_dir.mkdir(exist_ok=True)
        admin_init = admin_dir / "__init__.py"
        if not admin_init.exists():
            from setup.file_utils import write_file
            write_file(admin_init, _ADMIN_INIT)
            rollback.register_new_file(admin_init)

        # Patch app/__init__.py
        init = ROOT / "app" / "__init__.py"
        content = read_file(init)
        if "from app.admin" not in content:
            snippet = (
                "\n    if app.config.get(\"DB_ENABLED\"):\n"
                "        from app.admin import init_admin\n"
                "        from app.extensions import admin as _admin\n"
                "        _admin.name = app.config.get(\"PROJECT_NAME\", \"Admin\")\n"
                "        init_admin(app, _admin)\n"
            )
            # Inject before the return statement of create_app
            content = content.replace("    return app\n", snippet + "    return app\n", 1)
            write_file(init, content)
