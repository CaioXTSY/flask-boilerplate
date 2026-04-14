from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_file(path: Path, content: str) -> None:
    """Atomic write via temp file → rename. Creates parent dirs automatically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".setup_tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def inject_after(content: str, anchor: str, snippet: str) -> str:
    """Insert snippet immediately after the first line containing anchor."""
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if anchor in line:
            lines.insert(i + 1, snippet if snippet.endswith("\n") else snippet + "\n")
            return "".join(lines)
    return content


def inject_before(content: str, anchor: str, snippet: str) -> str:
    """Insert snippet immediately before the first line containing anchor."""
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if anchor in line:
            lines.insert(i, snippet if snippet.endswith("\n") else snippet + "\n")
            return "".join(lines)
    return content


def remove_lines_containing(content: str, substrings: list[str]) -> str:
    """Remove all lines that contain any of the given substrings.
    Collapses multiple consecutive blank lines into one."""
    lines = content.splitlines(keepends=True)
    filtered = [l for l in lines if not any(s in l for s in substrings)]
    out: list[str] = []
    prev_blank = False
    for line in filtered:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        out.append(line)
        prev_blank = is_blank
    return "".join(out)


_JINJA_INC = re.compile(r"\{%-?\s*(if|for|with|block|macro)\b")
_JINJA_DEC = re.compile(r"\{%-?\s*(endif|endfor|endwith|endblock|endmacro)\b")


def remove_jinja_block(content: str, start_contains: str) -> str:
    """Remove a Jinja2 block starting with a line containing start_contains.

    Tracks nesting depth to find the correct closing tag.
    The surrounding blank lines are also collapsed.
    """
    lines = content.splitlines(keepends=True)
    result: list[str] = []
    depth = 0
    removing = False

    for line in lines:
        stripped = line.strip()
        if not removing:
            if start_contains in stripped:
                removing = True
                depth = 1
            else:
                result.append(line)
        else:
            inc = bool(_JINJA_INC.search(stripped))
            dec = bool(_JINJA_DEC.search(stripped))
            if inc and not dec:
                depth += 1
            elif dec and not inc:
                depth -= 1
                if depth == 0:
                    removing = False

    # Collapse consecutive blank lines left behind
    out: list[str] = []
    prev_blank = False
    for line in result:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        out.append(line)
        prev_blank = is_blank
    return "".join(out)


def remove_block(content: str, start_marker: str, end_marker: str) -> str:
    """Remove all lines between start_marker and end_marker (inclusive)."""
    lines = content.splitlines(keepends=True)
    result: list[str] = []
    inside = False
    for line in lines:
        if start_marker in line:
            inside = True
        if not inside:
            result.append(line)
        if inside and end_marker in line:
            inside = False
    return "".join(result)


def remove_function(content: str, decorator_or_def_contains: str) -> str:
    """Remove a top-level or module-level function/fixture starting at the line
    containing decorator_or_def_contains (decorator or def line).
    Ends when a new top-level def/class is found or EOF.
    """
    lines = content.splitlines(keepends=True)
    result: list[str] = []
    removing = False
    found_start = False

    for line in lines:
        if not found_start:
            if decorator_or_def_contains in line:
                found_start = True
                removing = True
                continue
            result.append(line)
        else:
            # Stop removing when we hit a new top-level function/class definition
            # (line starts at column 0 with def/class/@)
            stripped = line.strip()
            if stripped and not line[0].isspace() and (
                line.startswith("def ")
                or line.startswith("class ")
                or line.startswith("@")
            ):
                removing = False
                result.append(line)
            elif not removing:
                result.append(line)

    # Collapse trailing blank lines at end of file
    while result and result[-1].strip() == "":
        result.pop()
    if result:
        result.append("\n")

    return "".join(result)


def requirements_add(path: Path, package: str) -> None:
    """Append package to requirements.txt if not already present."""
    content = read_file(path)
    # Extract base package name (before version specifier)
    base = re.split(r"[><=!\[]", package)[0].strip().lower()
    if base in content.lower():
        return
    if not content.endswith("\n"):
        content += "\n"
    content += package + "\n"
    write_file(path, content)


def requirements_remove(path: Path, package_names: list[str]) -> None:
    """Remove packages from requirements.txt by base name (case-insensitive)."""
    content = read_file(path)
    lines = content.splitlines(keepends=True)
    result = []
    for line in lines:
        # Extract base name of the package on this line
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append(line)
            continue
        base = re.split(r"[><=!\[]", stripped)[0].strip().lower()
        if any(base == name.lower() for name in package_names):
            continue
        result.append(line)
    write_file(path, "".join(result))


def env_set(path: Path, key: str, value: str) -> None:
    """Set or replace a key=value line in a .env file."""
    if not path.exists():
        write_file(path, f"{key}={value}\n")
        return
    content = read_file(path)
    lines = content.splitlines(keepends=True)
    found = False
    result = []
    for line in lines:
        if line.startswith(f"{key}=") or line.startswith(f"{key} ="):
            result.append(f"{key}={value}\n")
            found = True
        else:
            result.append(line)
    if not found:
        if result and not result[-1].endswith("\n"):
            result.append("\n")
        result.append(f"{key}={value}\n")
    write_file(path, "".join(result))


def extensions_add(path: Path, import_line: str, instance_line: str) -> None:
    """Append an extension import + instance to extensions.py."""
    content = read_file(path)
    if instance_line.split("=")[0].strip() in content:
        return  # already present
    content = content.rstrip("\n") + "\n" + import_line + "\n" + instance_line + "\n"
    write_file(path, content)


def init_add_to_register_extensions(path: Path, init_line: str) -> None:
    """Inject `init_line` before the closing of _register_extensions."""
    content = read_file(path)
    if init_line.strip() in content:
        return
    # Inject before `login_manager.init_app(app)` — first init call in the function
    # as a safe anchor. If not found, inject before the function's return (or at end).
    anchor = "login_manager.init_app(app)"
    if anchor in content:
        content = inject_before(content, anchor, f"    {init_line}")
    else:
        # Fallback: append at end of _register_extensions body
        content = inject_after(content, "def _register_extensions", f"    {init_line}")
    write_file(path, content)
