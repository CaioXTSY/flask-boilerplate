from __future__ import annotations

import shutil
from pathlib import Path

from setup.file_utils import ROOT, read_file, remove_block, requirements_remove, write_file
from setup.modules.base import FeatureModule


class TestingModule(FeatureModule):
    name = "Test Suite"
    key = "testing"

    def ask(self, state, cli) -> None:
        state.use_testing = cli.confirm("Keep test suite (pytest)?", default=True)

    def plan(self, state) -> list[str]:
        if state.use_testing:
            return ["(KEEP) tests/ directory and pytest configuration"]
        return [
            "(REMOVE) tests/ directory",
            "(REMOVE) pytest, pytest-cov, pytest-flask from requirements-dev.txt",
            "(REMOVE) [tool.pytest.ini_options] from pyproject.toml",
        ]

    def files_touched(self, state) -> list[Path]:
        if state.use_testing:
            return []
        dev_req = ROOT / "requirements-dev.txt"
        pyproject = ROOT / "pyproject.toml"
        return [f for f in [dev_req, pyproject] if f.exists()]

    def apply(self, state, rollback) -> None:
        if state.use_testing:
            return

        tests_dir = ROOT / "tests"
        if tests_dir.exists():
            shutil.rmtree(tests_dir)

        dev_req = ROOT / "requirements-dev.txt"
        if dev_req.exists():
            requirements_remove(
                dev_req,
                ["pytest", "pytest-cov", "pytest-flask", "pytest-env", "faker"],
            )

        pyproject = ROOT / "pyproject.toml"
        if pyproject.exists():
            content = read_file(pyproject)
            content = remove_block(
                content,
                "[tool.pytest.ini_options]",
                "addopts =",
            )
            write_file(pyproject, content)
