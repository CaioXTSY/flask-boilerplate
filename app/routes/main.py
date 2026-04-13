from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template

from app.utils.decorators import db_login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@db_login_required
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/health")
def health():
    status: dict = {"status": "ok"}

    if current_app.config.get("DB_ENABLED"):
        try:
            from app.extensions import db
            from sqlalchemy import text

            db.session.execute(text("SELECT 1"))
            status["db"] = "ok"
        except Exception as exc:
            current_app.logger.error("Health check DB failure: %s", exc)
            status["status"] = "unhealthy"
            status["db"] = "unreachable"
            return jsonify(status), 503

    return jsonify(status), 200
