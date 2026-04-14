from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from setup.rollback import Rollback
    from setup.state import SetupState
    from setup.cli import CLI

ROOT = Path(__file__).parent.parent.parent


class FeatureModule(ABC):
    name: str = ""           # Human-readable label: "Rate Limiting"
    key: str = ""            # snake_case id:        "rate_limiting"
    requires: list[str] = []  # keys of other modules that must be enabled
    optional: bool = True    # False = always applied (e.g. project_name, database)

    @abstractmethod
    def ask(self, state: "SetupState", cli: "CLI") -> None:
        """Collect answers interactively; populate state fields."""

    @abstractmethod
    def plan(self, state: "SetupState") -> list[str]:
        """Return list of human-readable action strings shown in the summary."""

    @abstractmethod
    def apply(self, state: "SetupState", rollback: "Rollback") -> None:
        """Perform all file system changes. Must be idempotent."""

    def files_touched(self, state: "SetupState") -> list[Path]:
        """Return paths that apply() will modify (for pre-snapshotting)."""
        return []
