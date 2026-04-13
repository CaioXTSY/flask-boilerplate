from __future__ import annotations

import logging
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

_SQLITE_OPTIONS: dict = {
    "connect_args": {"check_same_thread": False},
}
_MYSQL_OPTIONS: dict = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
_POSTGRES_OPTIONS: dict = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": 5,
    "max_overflow": 10,
}

_INSECURE_DEFAULT_KEY = "dev-key-change-me"


def _engine_options(uri: str | None) -> dict:
    if not uri:
        return {}
    if uri.startswith("sqlite"):
        return _SQLITE_OPTIONS
    if "mysql" in uri:
        return _MYSQL_OPTIONS
    if "postgresql" in uri or "postgres" in uri:
        return _POSTGRES_OPTIONS
    return {}


class Config:
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or _INSECURE_DEFAULT_KEY
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    AUTO_CREATE_TABLES: bool = False
    WTF_CSRF_ENABLED: bool = True

    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    REMEMBER_COOKIE_HTTPONLY: bool = True
    REMEMBER_COOKIE_SAMESITE: str = "Lax"

    SQLALCHEMY_DATABASE_URI: str | None = os.environ.get("DATABASE_URL")
    DB_ENABLED: bool = SQLALCHEMY_DATABASE_URI is not None
    SQLALCHEMY_ENGINE_OPTIONS: dict = _engine_options(SQLALCHEMY_DATABASE_URI)

    @staticmethod
    def init_app(app) -> None:
        pass


class DevelopmentConfig(Config):
    DEBUG: bool = True
    AUTO_CREATE_TABLES: bool = True
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "DEBUG")

    SESSION_COOKIE_SECURE: bool = False
    REMEMBER_COOKIE_SECURE: bool = False

    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'dev.db'}",
    )
    DB_ENABLED: bool = True
    SQLALCHEMY_ENGINE_OPTIONS: dict = _engine_options(SQLALCHEMY_DATABASE_URI)

    @staticmethod
    def init_app(app) -> None:
        Config.init_app(app)
        if not os.environ.get("SECRET_KEY"):
            logging.getLogger(__name__).warning(
                "SECRET_KEY not set — using insecure default key. "
                "Set SECRET_KEY env var before deploying."
            )


class TestingConfig(Config):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    DB_ENABLED: bool = True
    WTF_CSRF_ENABLED: bool = False
    AUTO_CREATE_TABLES: bool = True
    SECRET_KEY: str = "testing-secret-key"
    LOG_LEVEL: str = "CRITICAL"
    SQLALCHEMY_ENGINE_OPTIONS: dict = _engine_options("sqlite:///:memory:")

    SESSION_COOKIE_SECURE: bool = False
    REMEMBER_COOKIE_SECURE: bool = False


class ProductionConfig(Config):
    DEBUG: bool = False
    TESTING: bool = False

    SESSION_COOKIE_SECURE: bool = True
    REMEMBER_COOKIE_SECURE: bool = True

    SQLALCHEMY_DATABASE_URI: str | None = os.environ.get("DATABASE_URL")
    DB_ENABLED: bool = SQLALCHEMY_DATABASE_URI is not None
    SQLALCHEMY_ENGINE_OPTIONS: dict = _engine_options(SQLALCHEMY_DATABASE_URI)

    @classmethod
    def init_app(cls, app) -> None:
        Config.init_app(app)
        if not os.environ.get("SECRET_KEY"):
            raise RuntimeError(
                "SECRET_KEY environment variable is not set. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )


config: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
