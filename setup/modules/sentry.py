from __future__ import annotations

from pathlib import Path

from setup.file_utils import ROOT, env_set, inject_after, read_file, requirements_add, write_file
from setup.modules.base import FeatureModule

_SENTRY_SNIPPET = """\
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ""),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
)

"""


class SentryModule(FeatureModule):
    name = "Sentry Error Tracking"
    key = "sentry"

    def ask(self, state, cli) -> None:
        state.use_sentry = cli.confirm("Add Sentry error tracking?", default=False)
        if state.use_sentry:
            state.sentry_dsn = cli.prompt(
                "Sentry DSN (leave blank to configure later)",
                default="",
            )

    def plan(self, state) -> list[str]:
        if not state.use_sentry:
            return []
        return [
            "(ADD) sentry-sdk[flask] to requirements.txt",
            "(ADD) sentry_sdk.init() at top of create_app() in app/__init__.py",
            "(ADD) SENTRY_DSN to .env",
        ]

    def files_touched(self, state) -> list[Path]:
        if not state.use_sentry:
            return []
        return [ROOT / "requirements.txt", ROOT / "app" / "__init__.py", ROOT / ".env"]

    def apply(self, state, rollback) -> None:
        if not state.use_sentry:
            return

        requirements_add(ROOT / "requirements.txt", "sentry-sdk[flask]>=2.0,<3.0")

        init = ROOT / "app" / "__init__.py"
        content = read_file(init)
        if "sentry_sdk" not in content:
            # Inject after the `import os` line at the top of the file
            content = inject_after(content, "import os\n", _SENTRY_SNIPPET)
            write_file(init, content)

        env_set(ROOT / ".env", "SENTRY_DSN", state.sentry_dsn)
