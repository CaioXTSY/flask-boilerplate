from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or "dev-key-change-me"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    AUTO_CREATE_TABLES: bool = False
    WTF_CSRF_ENABLED: bool = True

    @staticmethod
    def init_app(app) -> None:
        pass


class DevelopmentConfig(Config):
    DEBUG: bool = True
    AUTO_CREATE_TABLES: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/meu_app?charset=utf8mb4",
    )
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "DEBUG")


class TestingConfig(Config):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False
    AUTO_CREATE_TABLES: bool = True
    SECRET_KEY: str = "testing-secret-key"
    LOG_LEVEL: str = "CRITICAL"


class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app) -> None:
        Config.init_app(app)

        secret_key = os.environ.get("SECRET_KEY")
        database_url = os.environ.get("DATABASE_URL")

        if not secret_key:
            raise RuntimeError("SECRET_KEY environment variable is not set.")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable is not set.")

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL", "")
    DEBUG: bool = False
    TESTING: bool = False


config: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
