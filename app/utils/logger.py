from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, has_request_context, g

from config import BASE_DIR

LOG_FORMAT = (
    "%(asctime)s %(levelname)s [%(name)s] [%(request_id)s] "
    "%(message)s [in %(pathname)s:%(lineno)d]"
)


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = g.get("request_id", "-") if has_request_context() else "-"
        return True


def configure_logging(app: Flask) -> None:
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    request_id_filter = _RequestIdFilter()

    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    file_handler.setLevel(log_level)
    file_handler.addFilter(request_id_filter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    stream_handler.setLevel(log_level)
    stream_handler.addFilter(request_id_filter)

    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)

    app.logger.info("Application startup")
