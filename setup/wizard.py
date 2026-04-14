from __future__ import annotations

from setup.cli import CLI
from setup.state import SetupState


def run_wizard(cli: CLI, state: SetupState) -> None:
    cli.banner("Flask Boilerplate  ·  Project Setup Wizard")
    cli.info("Answer each question to configure your project.")
    cli.info("Press Enter to accept the default shown in [brackets].\n")

    # ── PROJECT ───────────────────────────────────────────────────────────────
    cli.section("PROJECT")
    from setup.modules.project_name import ProjectNameModule
    ProjectNameModule().ask(state, cli)

    # ── DATABASE ──────────────────────────────────────────────────────────────
    cli.section("DATABASE")
    from setup.modules.database import DatabaseModule
    DatabaseModule().ask(state, cli)

    # ── FEATURES ──────────────────────────────────────────────────────────────
    cli.section("FEATURES")

    from setup.modules.authentication import AuthenticationModule
    AuthenticationModule().ask(state, cli)

    from setup.modules.admin_panel import AdminPanelModule
    AdminPanelModule().ask(state, cli)

    from setup.modules.email_support import EmailSupportModule
    EmailSupportModule().ask(state, cli)

    from setup.modules.rate_limiting import RateLimitingModule
    RateLimitingModule().ask(state, cli)

    from setup.modules.cors import CORSModule
    CORSModule().ask(state, cli)

    from setup.modules.api_mode import APIModeModule
    APIModeModule().ask(state, cli)

    from setup.modules.security_headers import SecurityHeadersModule
    SecurityHeadersModule().ask(state, cli)

    from setup.modules.sentry import SentryModule
    SentryModule().ask(state, cli)

    # ── DEPENDENCY ENFORCEMENT ────────────────────────────────────────────────
    _enforce_dependencies(state, cli)

    # ── DEVOPS ────────────────────────────────────────────────────────────────
    cli.section("DEVOPS")

    from setup.modules.docker import DockerModule
    DockerModule().ask(state, cli)

    from setup.modules.cicd import CICDModule
    CICDModule().ask(state, cli)

    # ── TESTING ───────────────────────────────────────────────────────────────
    cli.section("TESTING")

    from setup.modules.testing import TestingModule
    TestingModule().ask(state, cli)


def _enforce_dependencies(state: SetupState, cli: CLI) -> None:
    """Automatically disable features whose dependencies weren't selected."""
    if state.db_backend == "none" and state.use_auth:
        state.use_auth = False
        cli.warn("Authentication disabled — no database backend was selected.")

    if not state.use_auth:
        if state.use_admin:
            state.use_admin = False
            cli.warn("Admin panel disabled — requires authentication.")
        if state.use_rate_limiting:
            state.use_rate_limiting = False
            cli.warn("Rate limiting disabled — requires authentication.")
