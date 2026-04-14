from __future__ import annotations

from pathlib import Path

from setup.file_utils import ROOT
from setup.modules.base import FeatureModule


class DockerModule(FeatureModule):
    name = "Docker"
    key = "docker"

    def ask(self, state, cli) -> None:
        state.use_docker = cli.confirm("Keep Docker files?", default=True)

    def plan(self, state) -> list[str]:
        if state.use_docker:
            return ["(KEEP) Dockerfile, docker-entrypoint.sh"]
        return ["(REMOVE) Dockerfile, docker-entrypoint.sh"]

    def files_touched(self, state) -> list[Path]:
        return [ROOT / "Dockerfile", ROOT / "docker-entrypoint.sh"]

    def apply(self, state, rollback) -> None:
        if state.use_docker:
            return
        for fname in ("Dockerfile", "docker-entrypoint.sh", ".dockerignore"):
            p = ROOT / fname
            p.unlink(missing_ok=True)
