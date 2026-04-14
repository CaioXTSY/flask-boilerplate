from __future__ import annotations

from pathlib import Path

from setup.file_utils import ROOT, write_file
from setup.modules.base import FeatureModule

_WORKFLOW_TEMPLATE = """\
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python {python_version}
        uses: actions/setup-python@v5
        with:
          python-version: "{python_version}"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Lint (ruff)
        run: ruff check .

      - name: Format check (black)
        run: black --check .

      - name: Run tests
        run: pytest
        env:
          FLASK_ENV: testing
"""


class CICDModule(FeatureModule):
    name = "GitHub Actions CI"
    key = "cicd"

    def ask(self, state, cli) -> None:
        state.use_cicd = cli.confirm("Generate GitHub Actions CI workflow?", default=False)
        if state.use_cicd:
            import re
            def _validate_pyver(v: str) -> str | None:
                if not re.match(r"^\d+\.\d+$", v):
                    return f"Use format MAJOR.MINOR (e.g. 3.12), got: {v!r}"
                return None
            state.ci_python_version = cli.prompt(
                "Python version", default="3.12", validator=_validate_pyver
            )

    def plan(self, state) -> list[str]:
        if not state.use_cicd:
            return []
        return [
            f"(ADD) .github/workflows/test.yml  (Python {state.ci_python_version}, ruff + black + pytest)",
        ]

    def files_touched(self, state) -> list[Path]:
        return []  # only creates new files

    def apply(self, state, rollback) -> None:
        if not state.use_cicd:
            return

        workflow_dir = ROOT / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = workflow_dir / "test.yml"
        if not workflow_file.exists():
            content = _WORKFLOW_TEMPLATE.format(python_version=state.ci_python_version)
            write_file(workflow_file, content)
            rollback.register_new_file(workflow_file)
