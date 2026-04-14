from __future__ import annotations

import os
import shutil
import sys
from getpass import getpass
from typing import Callable

_NO_COLOR = bool(os.getenv("NO_COLOR")) or not sys.stdout.isatty()


def _c(code: str) -> str:
    return "" if _NO_COLOR else code


RESET  = _c("\033[0m")
BOLD   = _c("\033[1m")
DIM    = _c("\033[2m")
RED    = _c("\033[91m")
GREEN  = _c("\033[92m")
YELLOW = _c("\033[93m")
CYAN   = _c("\033[96m")

CHECK  = f"{GREEN}✓{RESET}"
CROSS  = f"{RED}✗{RESET}"
WARN_S = f"{YELLOW}!{RESET}"
ARROW  = f"{CYAN}→{RESET}"
BULLET = f"{DIM}•{RESET}"


class CLI:
    def banner(self, title: str) -> None:
        width = min(shutil.get_terminal_size().columns, 62)
        border = "═" * (width - 2)
        print(f"\n{BOLD}{CYAN}╔{border}╗{RESET}")
        padded = title.center(width - 2)
        print(f"{BOLD}{CYAN}║{padded}║{RESET}")
        print(f"{BOLD}{CYAN}╚{border}╝{RESET}\n")

    def section(self, title: str) -> None:
        width = min(shutil.get_terminal_size().columns, 60)
        line = "─" * max(0, width - len(title) - 5)
        print(f"\n  {BOLD}{title}{RESET}  {DIM}{line}{RESET}\n")

    def success(self, text: str) -> None:
        print(f"  {CHECK} {text}")

    def info(self, text: str) -> None:
        print(f"  {ARROW} {text}")

    def warn(self, text: str) -> None:
        print(f"  {WARN_S} {YELLOW}{text}{RESET}")

    def error(self, text: str) -> None:
        print(f"  {CROSS} {RED}{text}{RESET}")

    def step(self, text: str) -> None:
        print(f"  {BULLET} {DIM}{text}…{RESET}", flush=True)

    def done(self, text: str) -> None:
        print(f"  {CHECK} {GREEN}{text}{RESET}")

    def plan_item(self, verb: str, text: str) -> None:
        color = GREEN if verb in ("ADD", "CONFIGURE") else YELLOW
        print(f"    {color}{verb:<12}{RESET} {text}")

    def prompt(
        self,
        question: str,
        default: str | None = None,
        validator: Callable[[str], str | None] | None = None,
        secret: bool = False,
    ) -> str:
        hint = f" [{DIM}{default}{RESET}]" if default is not None else ""
        while True:
            try:
                if secret:
                    value = getpass(f"  {question}{hint}: ").strip()
                else:
                    value = input(f"  {question}{hint}: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                raise SystemExit(0)
            if not value:
                if default is not None:
                    value = default
                else:
                    print(f"  {WARN_S} {YELLOW}Value required.{RESET}")
                    continue
            if validator:
                err = validator(value)
                if err:
                    print(f"  {WARN_S} {YELLOW}{err}{RESET}")
                    continue
            return value

    def choose(
        self,
        question: str,
        options: list[tuple[str, str]],
        default: int = 1,
    ) -> str:
        """Numbered menu. options = list of (label, value). Returns chosen value."""
        print(f"  {question}")
        for i, (label, _) in enumerate(options, 1):
            marker = f"{CYAN}→{RESET}" if i == default else " "
            print(f"    {marker} [{i}] {label}")
        while True:
            try:
                raw = input(f"  Choice [{DIM}{default}{RESET}]: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                raise SystemExit(0)
            if not raw:
                return options[default - 1][1]
            if raw.isdigit() and 1 <= int(raw) <= len(options):
                return options[int(raw) - 1][1]
            print(f"  {WARN_S} {YELLOW}Enter a number between 1 and {len(options)}.{RESET}")

    def prompt_int(
        self,
        question: str,
        default: int,
        min_val: int = 1,
        max_val: int = 65535,
    ) -> int:
        """Like prompt(), but validates and returns an integer."""
        def _validate(value: str) -> str | None:
            if not value.isdigit():
                return f"Must be a number (got: {value!r})"
            n = int(value)
            if not (min_val <= n <= max_val):
                return f"Must be between {min_val} and {max_val}"
            return None

        raw = self.prompt(question, default=str(default), validator=_validate)
        return int(raw)

    def confirm(self, question: str, default: bool = True) -> bool:
        hint = f"[{BOLD}Y{RESET}/n]" if default else f"[y/{BOLD}N{RESET}]"
        try:
            raw = input(f"  {question} {hint}: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            raise SystemExit(0)
        if not raw:
            return default
        return raw in ("y", "yes")
