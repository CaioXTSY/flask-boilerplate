# Project Overview

Flask Boilerplate is a production-ready starter for server-rendered Python web applications. It ships with
session-based authentication (Flask-Login), CSRF protection (Flask-WTF), SQLAlchemy ORM with Alembic
migrations, structured request-ID logging, and a Gunicorn/Docker deployment path—so teams can skip
the plumbing and go straight to feature work. The database layer is optional: omitting `DATABASE_URL`
disables auth and ORM entirely, leaving a lightweight no-DB web server.

---

## Repository Structure

```
flask-boilerplate/
├── app/                  # Application package (all runtime code lives here)
│   ├── __init__.py       # App factory: create_app()
│   ├── extensions.py     # SQLAlchemy, Migrate, LoginManager, CSRFProtect singletons
│   ├── errors/           # Error blueprints and HTTP error handlers (403, 404, 500)
│   ├── forms/            # Flask-WTF form classes (auth_forms.py)
│   ├── models/           # SQLAlchemy model definitions (user.py)
│   ├── routes/           # Blueprint route handlers (main.py, auth.py)
│   ├── static/           # CSS, JS, and image assets
│   ├── templates/        # Jinja2 HTML templates (base.html + per-view)
│   └── utils/            # Cross-cutting utilities: logger, middleware, decorators
├── config.py             # Config classes: Development / Testing / Production
├── docs/                 # Supplementary developer documentation (Markdown)
├── migrations/           # Alembic migration scripts (auto-managed by Flask-Migrate)
├── tests/                # Pytest suite: conftest, test_auth, test_main
├── instance/             # Runtime artefacts ignored by git (SQLite dev.db, etc.)
├── logs/                 # Rotating log files (app.log) — git-ignored
├── Dockerfile            # Multi-stage production image (python:3.12-slim + gunicorn)
├── pyproject.toml        # Black, Ruff, and Pytest configuration
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Dev/test extras (pytest, black, ruff, mypy, faker)
├── run.py                # `flask run` entry-point for development
└── wsgi.py               # WSGI entry-point for gunicorn / production servers
```

---

## Build & Development Commands

### Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env              # then edit .env to set SECRET_KEY / DATABASE_URL
```

### Run (development)

```bash
flask run                         # uses .flaskenv → FLASK_ENV=development
# or
python run.py
```

### Database migrations

```bash
flask db init                     # first time only — creates migrations/ directory
flask db migrate -m "description" # generate a new revision
flask db upgrade                  # apply pending migrations
flask db downgrade                # roll back one revision
```

### Lint & format

```bash
ruff check .                      # fast lint (E, F, W, I, B, UP rules)
ruff check . --fix                # auto-fix safe issues
black .                           # format all Python files
black --check .                   # check without writing
```

### Type-check

```bash
mypy app config                   # static type analysis
```

### Test

```bash
pytest                            # run full suite (quiet, short-tb)
pytest --cov=app --cov-report=term-missing   # with coverage
pytest tests/test_auth.py -v      # single module, verbose
```

### Docker

```bash
docker build -t flask-boilerplate .
docker run -p 8000:8000 \
  -e SECRET_KEY=<secret> \
  -e DATABASE_URL=<url> \
  flask-boilerplate
```

### Production (gunicorn directly)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 \
  --access-logfile - --error-logfile - wsgi:app
```

---

## Code Style & Conventions

| Concern         | Rule                                                                 |
|-----------------|----------------------------------------------------------------------|
| Formatter       | **Black** — line length 100, target Python 3.11                     |
| Linter          | **Ruff** — rules E, F, W, I, B, UP; B008 suppressed                 |
| Import order    | `known-first-party = ["app", "config"]` (ruff/isort)                |
| Type hints      | `from __future__ import annotations` at every module top            |
| Naming          | `snake_case` for vars/functions, `PascalCase` for classes           |
| Blueprints      | One blueprint per concern, registered in `create_app()`              |
| Models          | One model per file in `app/models/`; file name matches model name   |
| Forms           | Defined in `app/forms/`; one file per domain (e.g. `auth_forms.py`) |
| Templates       | Mirror route structure — `auth/login.html` for `auth_bp`            |

**Commit message template:**

```
<type>: <short imperative summary>          # ≤ 72 chars

[optional body — why, not what]
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`.

---

## Architecture Notes

```
Browser
  │  HTTPS
  ▼
Gunicorn (4 workers, wsgi:app)
  │
  ▼
Flask App (create_app factory)
  ├─ Middleware (before/after_request)
  │   └─ Injects g.request_id, logs method/path/status/duration
  ├─ CSRF (Flask-WTF) — protects all POST/PUT/DELETE
  ├─ LoginManager (Flask-Login) — session cookie auth
  ├─ Blueprints
  │   ├─ main_bp      /           — public pages (index, about, dashboard)
  │   ├─ auth_bp      /auth/*     — register, login, logout (DB_ENABLED only)
  │   └─ errors_bp    —           — 403 / 404 / 500 handlers
  └─ SQLAlchemy → Database (SQLite | MySQL | PostgreSQL)
```

**Key design decisions:**

- **App factory** (`create_app`) keeps the module importable without side-effects; `FLASK_ENV`
  selects the config class (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`).
- **DB_ENABLED flag**: if `DATABASE_URL` is absent the ORM, migrations, and auth blueprint are
  never registered — the app runs as a pure static/template server.
- **Extensions singleton** (`app/extensions.py`): all Flask extensions are instantiated once without
  an app object, then bound via `init_app()` to avoid circular imports.
- **Request-ID middleware** stamps every request with a UUID (or echoes `X-Request-ID` from a
  reverse proxy) and threads it through the structured log format.
- **Logging**: `RotatingFileHandler` (10 MB × 5 backups) + `StreamHandler`, both filtered by
  `_RequestIdFilter`; suppressed during `TESTING=True`.

---

## Testing Strategy

### Tools

| Tool          | Purpose                                      |
|---------------|----------------------------------------------|
| pytest        | Test runner                                  |
| pytest-flask  | `client`, `app` fixtures, request context    |
| pytest-cov    | Coverage reporting                           |
| faker         | Synthetic data generation                    |

### Fixtures (`tests/conftest.py`)

| Fixture      | Scope    | Description                                          |
|--------------|----------|------------------------------------------------------|
| `app`        | session  | Creates testing app; sets up and tears down DB once  |
| `db`         | function | Yields DB; truncates all tables after each test      |
| `client`     | function | Flask test client (anonymous)                        |
| `runner`     | function | Flask CLI runner                                     |
| `auth_client`| function | Pre-authenticated client with a seeded `testuser`    |

### Running in CI

```bash
FLASK_ENV=testing pytest --cov=app --cov-report=xml
```

- `TestingConfig` uses an in-memory SQLite DB; `WTF_CSRF_ENABLED=False`.
- No external services are required.

---

## Security & Compliance

### Secrets

- **Never commit** `.env` — it is git-ignored. Use `.env.example` as a template.
- `SECRET_KEY` is required at runtime in production; `ProductionConfig.init_app()` raises
  `RuntimeError` if it is absent.
- Generate a strong key: `python -c "import secrets; print(secrets.token_hex(32))"`.

### Session & cookie hardening

| Setting                    | Dev     | Prod   |
|----------------------------|---------|--------|
| `SESSION_COOKIE_HTTPONLY`  | True    | True   |
| `SESSION_COOKIE_SECURE`    | False   | True   |
| `SESSION_COOKIE_SAMESITE`  | Lax     | Lax    |
| `REMEMBER_COOKIE_SECURE`   | False   | True   |

### CSRF

All state-changing requests are protected by Flask-WTF's `CSRFProtect`. Disabled only in
`TestingConfig`. Logout uses `POST` (not `GET`) to prevent CSRF-driven logout.

### Password storage

Passwords are hashed with `werkzeug.security.generate_password_hash` (PBKDF2-HMAC-SHA256).
Plain-text passwords are never stored or logged.

### Open-redirect guard

The login redirect validates that `next` is a relative URL (`urlsplit(next).netloc == ""`).

### Dependency scanning

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

### Licenses

All direct dependencies use MIT, BSD, or PSF licenses. Verify with:

```bash
pip-licenses --order=license
```

---

## Agent Guardrails

Automated agents (CI bots, coding assistants, LLM-driven tools) **must** observe the following:

1. **Never modify** `.env` or any file that may contain real secrets.
2. **Never commit directly to `main`**; all changes require a pull request.
3. **Never run** `flask db upgrade` or destructive SQL against a production database without
   explicit human approval.
4. **Never delete** migration files in `migrations/versions/` — reverting a migration is done via
   `flask db downgrade`, not file deletion.
5. **Do not** disable or bypass CSRF (`WTF_CSRF_ENABLED=False`) outside of `TestingConfig`.
6. **Do not** lower cookie security settings (`SECURE`, `HTTPONLY`, `SAMESITE`) in any config
   other than `DevelopmentConfig`.
7. **Always run** `ruff check . && black --check . && pytest` before proposing a PR.
8. **Do not** add `print()` statements to application code — use `app.logger` instead.
9. **Human review required** for any change to: `config.py`, `app/extensions.py`,
   `app/models/user.py`, `Dockerfile`, `migrations/`.

---

## Extensibility Hooks

### Environment variables

| Variable       | Default              | Effect                                          |
|----------------|----------------------|-------------------------------------------------|
| `FLASK_ENV`    | `development`        | Selects config class (`development`/`production`/`testing`) |
| `SECRET_KEY`   | `dev-key-change-me`  | Flask session signing key; **must** be set in prod |
| `DATABASE_URL` | *(empty)*            | SQLAlchemy URI; omit to disable DB & auth        |
| `LOG_LEVEL`    | `INFO` (`DEBUG` dev) | Python logging level                            |

### Adding a new blueprint

1. Create `app/routes/<name>.py` with a `Blueprint` named `<name>_bp`.
2. Import and register it in `app/__init__.py → _register_blueprints()`.
3. Add corresponding templates under `app/templates/<name>/`.

### Adding a new model

1. Create `app/models/<name>.py` with a `db.Model` subclass.
2. Import the model in `app/__init__.py` (or `app/models/__init__.py`) so SQLAlchemy discovers it.
3. Run `flask db migrate -m "add <name> table" && flask db upgrade`.

### Adding a new form

1. Create or extend a file in `app/forms/`.
2. Import the form in the relevant route file.

### Custom decorators

`app/utils/decorators.py` contains `db_login_required` — a guard that returns 503 when the database
is disabled. Add additional cross-cutting decorators here and import them in routes.

---

## Further Reading

- [docs/project-overview.md](docs/project-overview.md) — goals, constraints, and design decisions
- [docs/add-feature.md](docs/add-feature.md) — step-by-step guide for adding a new feature
- [docs/auth-and-security.md](docs/auth-and-security.md) — deep dive into auth flow and security
- [docs/database.md](docs/database.md) — database setup, migrations, and multi-DB support
- [Flask documentation](https://flask.palletsprojects.com/) — upstream reference
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) — ORM integration
- [Flask-Migrate](https://flask-migrate.readthedocs.io/) — Alembic migration wrapper
