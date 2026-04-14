from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class SetupState:
    # ── Project ───────────────────────────────────────────────────────────────
    project_name: str = "my-app"

    # ── Database ──────────────────────────────────────────────────────────────
    db_backend: Literal["sqlite", "mysql", "postgresql", "none"] = "sqlite"
    db_host: str = "localhost"
    db_port: str = ""
    db_name: str = "app"
    db_user: str = "app"
    db_password: str = ""

    # ── Features ──────────────────────────────────────────────────────────────
    use_auth: bool = True
    use_admin: bool = False
    use_email: bool = False
    use_rate_limiting: bool = False
    use_cors: bool = False
    use_api_mode: bool = False
    use_security_headers: bool = False
    use_sentry: bool = False

    # ── DevOps ────────────────────────────────────────────────────────────────
    use_docker: bool = True
    use_cicd: bool = False

    # ── Testing ───────────────────────────────────────────────────────────────
    use_testing: bool = True

    # ── Extra module config ───────────────────────────────────────────────────
    sentry_dsn: str = ""
    mail_server: str = "localhost"
    mail_port: int = 1025
    cors_origins: str = "*"
    ci_python_version: str = "3.12"

    # ── Internal bookkeeping ──────────────────────────────────────────────────
    applied_modules: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def db_url(self) -> str:
        """Build the DATABASE_URL connection string from current state."""
        if self.db_backend == "none":
            return ""
        if self.db_backend == "sqlite":
            return "sqlite:///instance/dev.db"
        port = self.db_port or ("3306" if self.db_backend == "mysql" else "5432")
        if self.db_backend == "mysql":
            return (
                f"mysql+pymysql://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{port}/{self.db_name}?charset=utf8mb4"
            )
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{port}/{self.db_name}"
        )

    def db_url_redacted(self) -> str:
        """db_url() with password replaced by ***."""
        url = self.db_url()
        if self.db_password:
            url = url.replace(self.db_password, "***")
        return url
