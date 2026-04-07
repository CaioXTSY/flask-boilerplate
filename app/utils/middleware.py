from __future__ import annotations

import time
import uuid

from flask import Flask, g, request


def register_middleware(app: Flask) -> None:
    @app.before_request
    def _start_request() -> None:
        g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        g.request_start = time.perf_counter()

    @app.after_request
    def _finish_request(response):
        elapsed_ms = (time.perf_counter() - g.request_start) * 1000
        response.headers["X-Request-ID"] = g.request_id

        app.logger.info(
            "%s %s %s %.2fms",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
            extra={"request_id": g.request_id},
        )

        return response
