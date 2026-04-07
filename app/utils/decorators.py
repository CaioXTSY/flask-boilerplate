from __future__ import annotations

from functools import wraps

from flask import abort, current_app
from flask_login import login_required


def db_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get("DB_ENABLED"):
            abort(503)
        return login_required(f)(*args, **kwargs)

    return decorated_function
