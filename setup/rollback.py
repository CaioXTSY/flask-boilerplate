from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent


class Rollback:
    def __init__(self) -> None:
        ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        self.backup_dir = ROOT / ".setup-backup" / ts
        self._manifest: list[str] = []
        self._new_files: list[str] = []  # files created by apply() — delete on restore

    def snapshot(self, paths: list[Path]) -> None:
        """Copy all existing files to backup directory before any changes."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        for path in paths:
            if not path.exists() or not path.is_file():
                continue
            rel = str(path.relative_to(ROOT))
            dest = self.backup_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            self._manifest.append(rel)
        manifest_path = self.backup_dir / "manifest.json"
        manifest_path.write_text(json.dumps(self._manifest, indent=2), encoding="utf-8")

    def register_new_file(self, path: Path) -> None:
        """Track a file created (not pre-existing) so it can be deleted on restore."""
        self._new_files.append(str(path.relative_to(ROOT)))

    def restore(self) -> None:
        """Restore all snapshotted files to their original locations
        and delete any files that were created during apply()."""
        for rel in self._manifest:
            src = self.backup_dir / rel
            dst = ROOT / rel
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        for rel in self._new_files:
            p = ROOT / rel
            if p.exists():
                p.unlink(missing_ok=True)

    def backup_path(self) -> str:
        return str(self.backup_dir)
