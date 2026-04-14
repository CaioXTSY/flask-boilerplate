from __future__ import annotations

import re
from pathlib import Path

from setup.file_utils import ROOT, read_file, write_file
from setup.modules.base import FeatureModule


def _validate_name(value: str) -> str | None:
    if not re.match(r"^[a-z0-9][a-z0-9-]*$", value):
        return "Use only lowercase letters, numbers, and hyphens (e.g. my-app)"
    return None


class ProjectNameModule(FeatureModule):
    name = "Project Name"
    key = "project_name"
    optional = False

    def ask(self, state, cli) -> None:
        state.project_name = cli.prompt(
            "Project name",
            default="my-app",
            validator=_validate_name,
        )

    def plan(self, state) -> list[str]:
        return [f"(CONFIGURE) Rename project to \"{state.project_name}\" in templates and README"]

    def files_touched(self, state) -> list[Path]:
        return [
            ROOT / "app" / "templates" / "base.html",
            ROOT / "README.md",
        ]

    def apply(self, state, rollback) -> None:
        name = state.project_name
        title = name.replace("-", " ").title()

        # base.html — replace "App" in <title> default and navbar brand link
        base_html = ROOT / "app" / "templates" / "base.html"
        content = read_file(base_html)
        content = content.replace(
            "{% block title %}App{% endblock %}",
            f"{{% block title %}}{title}{{% endblock %}}",
        )
        content = content.replace(
            'class="font-semibold text-indigo-600">App</a>',
            f'class="font-semibold text-indigo-600">{title}</a>',
        )
        write_file(base_html, content)

        # README.md — replace first heading
        readme = ROOT / "README.md"
        if readme.exists():
            content = read_file(readme)
            content = re.sub(r"^# .+", f"# {title}", content, count=1, flags=re.MULTILINE)
            write_file(readme, content)
