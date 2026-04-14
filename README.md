# Flask Boilerplate

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

A production-ready Flask starter for building server-rendered web applications. Ships with session-based authentication, multi-database support, Alembic migrations, structured logging with request IDs, and a Docker-ready deployment path — so you can skip the boilerplate and focus on your product.

Configured once via an interactive setup wizard: `python setup.py`.

---

## Why this boilerplate?

Most Flask starters are either too minimal (just a hello world) or too opinionated (locked to one database, one auth strategy, one deployment model). This one ships with everything you need for production, and strips out anything you don't — through a guided wizard run once at project setup.

**Key design decisions:**

- **Optional database** — the app boots and serves pages without any database configured. ORM, migrations, and auth routes are only registered when `DATABASE_URL` is present.
- **Application factory** — `create_app()` keeps the module importable without side effects, enabling clean testing and multiple app instances.
- **No magic** — every feature is a standard Flask extension wired up explicitly. Reading the code teaches you Flask, not this framework.

---

## Features

- **Application Factory** pattern with environment-based configuration (dev / test / prod)
- **Authentication** — register, login, logout via Flask-Login with secure session cookies
- **CSRF protection** on all forms via Flask-WTF
- **Multi-backend database** — SQLite, MySQL, and PostgreSQL out of the box
- **Migrations** with Flask-Migrate (Alembic) — pre-initialized, auto-run on Docker startup
- **Health check** endpoint at `/health` with optional database connectivity probe
- **Structured logging** — rotating file handler + stdout, request ID on every line
- **Request tracing** — `X-Request-ID` injected and propagated through every log entry
- **Error pages** — 403, 404, 500 with automatic session rollback
- **Tailwind CSS** via CDN, no build step required
- **Docker** — non-root user, `HEALTHCHECK`, graceful shutdown, automatic migrations
- **Interactive setup wizard** — configure everything via `python setup.py` after cloning

---

## Tech Stack

| Layer | Library | Version |
|---|---|---|
| Web framework | Flask | `>=3.0` |
| ORM | SQLAlchemy + Flask-SQLAlchemy | `>=2.0` |
| Migrations | Flask-Migrate (Alembic) | `>=4.0` |
| Auth | Flask-Login | `>=0.6` |
| Forms & CSRF | Flask-WTF + WTForms | `>=1.2` |
| MySQL driver | PyMySQL + cryptography | `>=1.1` |
| PostgreSQL driver | psycopg2-binary | `>=2.9` |
| Password hashing | Werkzeug | `>=3.0` |
| Env loading | python-dotenv | `>=1.0` |
| WSGI server | Gunicorn | `>=21.2` |
| CSS | Tailwind CSS (CDN) | — |
| Testing | pytest + pytest-flask + pytest-env | `>=8.0` |

---

## Prerequisites

- Python **3.11** or higher
- pip
- (Optional) Docker, for containerized deployment
- (Optional) MySQL or PostgreSQL server, if not using SQLite

---

## Getting Started

### 1. Clone

```bash
git clone <repo-url> my-app
cd my-app
```

### 2. Create a virtual environment

```bash
# macOS / Linux
python -m venv .venv && source .venv/bin/activate

# Windows
python -m venv .venv && .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements-dev.txt
```

### 4. Run the setup wizard

```bash
python setup.py
```

The wizard asks about your database backend, which optional features to enable, and writes a fully populated `.env` — including a freshly generated `SECRET_KEY`. See [Setup Wizard](#setup-wizard) for a full walkthrough.

### 5. Apply database migrations

```bash
flask db migrate -m "initial schema"
flask db upgrade
```

Skip this step if you chose **No database** in the wizard.

### 6. Start the development server

```bash
flask run
```

Visit `http://localhost:5000`.

---

## Manual Setup (skip the wizard)

If you prefer to configure manually:

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```env
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=sqlite:///instance/dev.db
```

Then run migrations and start the server as above.

---

## Project Structure

```
.
├── app/
│   ├── __init__.py              # Application factory — create_app()
│   ├── extensions.py            # Extension instances (db, migrate, login_manager, csrf)
│   ├── models/
│   │   └── user.py              # User model + user_loader
│   ├── forms/
│   │   └── auth_forms.py        # LoginForm, RegisterForm
│   ├── routes/
│   │   ├── main.py              # Blueprint: /, /about, /dashboard, /health
│   │   └── auth.py              # Blueprint: /auth/register, /auth/login, /auth/logout
│   ├── errors/
│   │   └── handlers.py          # Global error handlers (403, 404, 500)
│   ├── utils/
│   │   ├── decorators.py        # db_login_required — login guard aware of DB_ENABLED
│   │   ├── logger.py            # RotatingFileHandler + request ID filter
│   │   └── middleware.py        # before/after request hooks (timing, X-Request-ID)
│   ├── templates/
│   │   ├── base.html            # Base layout with nav, flash messages, footer
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── about.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── errors/
│   │       ├── 403.html
│   │       ├── 404.html
│   │       └── 500.html
│   └── static/
│       ├── css/style.css        # Custom overrides (Tailwind handles the rest)
│       └── js/main.js           # Auto-dismiss flash messages
├── migrations/                  # Alembic migration files (pre-initialized)
│   └── versions/                # Generated migration scripts go here
├── setup/                       # Interactive project setup wizard
│   ├── cli.py                   # Terminal I/O: colors, prompts, menus
│   ├── state.py                 # SetupState dataclass flowing through all modules
│   ├── file_utils.py            # Atomic writes, line/block/Jinja removal helpers
│   ├── rollback.py              # File snapshot/restore — safety net before any write
│   ├── wizard.py                # Orchestrates questions, enforces dependencies
│   ├── runner.py                # Applies modules, generates .env, writes setup.log
│   └── modules/                 # One file per feature — ask / plan / apply / files_touched
│       ├── project_name.py
│       ├── database.py
│       ├── authentication.py
│       ├── admin_panel.py
│       ├── email_support.py
│       ├── rate_limiting.py
│       ├── cors.py
│       ├── api_mode.py
│       ├── security_headers.py
│       ├── sentry.py
│       ├── docker.py
│       ├── cicd.py
│       └── testing.py
├── setup.py                     # Entry point: python setup.py
├── tests/
│   ├── conftest.py              # Fixtures: app, db, client, runner, auth_client
│   ├── test_auth.py             # Auth flow tests
│   └── test_main.py             # Route tests
├── docs/
│   ├── project-overview.md      # Architecture decisions and conventions
│   ├── add-feature.md           # How to add a new feature module
│   ├── database.md              # Database guide (models, migrations, backends)
│   └── auth-and-security.md     # Auth flow, CSRF, cookie security
├── config.py                    # Config classes (Development, Testing, Production)
├── run.py                       # Dev entry point (respects FLASK_ENV)
├── wsgi.py                      # Production WSGI entry point (Gunicorn)
├── Dockerfile
├── docker-entrypoint.sh         # Runs migrations then starts Gunicorn
├── .env.example                 # Template — copy to .env and fill in values
├── .flaskenv                    # Sets FLASK_APP and FLASK_ENV for `flask` CLI
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Dev/test extras (pytest, black, ruff, mypy)
├── pyproject.toml               # Black, Ruff, and pytest configuration
└── AGENTS.md                    # Guardrails for AI coding agents
```

---

## Setup Wizard

`python setup.py` is an interactive CLI wizard that tailors the project to your needs. It runs once after cloning — no external dependencies beyond the Python standard library.

### What it configures

| Section | Options |
|---|---|
| **Project** | Project name (used in templates, README, Docker labels) |
| **Database** | SQLite / MySQL / PostgreSQL / None — collects host, port, credentials |
| **Authentication** | Keep or remove the full auth system (routes, forms, models, templates) |
| **Admin Panel** | Add Flask-Admin with a User model view at `/admin` |
| **Email** | Add Flask-Mail with dev (Mailhog) defaults |
| **Rate Limiting** | Add Flask-Limiter (10 req/min) on `/auth/login` and `/auth/register` |
| **CORS** | Add Flask-CORS with configurable allowed origins |
| **JSON API** | Scaffold a `/api/v1/` blueprint alongside the existing HTML routes |
| **Security Headers** | Add Flask-Talisman (CSP, HSTS, X-Frame-Options) |
| **Sentry** | Add Sentry SDK with Flask integration and configurable DSN |
| **Docker** | Keep or remove `Dockerfile` and `docker-entrypoint.sh` |
| **CI/CD** | Generate `.github/workflows/test.yml` (ruff + black + pytest) |
| **Testing** | Keep or remove the `tests/` directory and pytest config |

### Dependency enforcement

The wizard automatically disables incompatible combinations:

- Selecting **No database** disables Authentication, Admin Panel, and Rate Limiting
- Disabling **Authentication** disables Admin Panel and Rate Limiting
- A warning is printed whenever a choice is forced by a dependency

### Safety model

Before touching any file, the wizard:

1. Collects the full set of files that will be modified
2. Copies every existing file to `.setup-backup/<timestamp>/`
3. Applies all changes atomically (write to temp file → `os.replace`)
4. On any error, **automatically restores all files** from the backup
5. Writes `setup.log` with a timestamped record of every action taken

The backup directory is kept on disk after a successful run. Its path is printed at the end.

### Generated `.env`

After applying all changes, the wizard generates `.env` with:

- `SECRET_KEY` — a fresh `secrets.token_hex(32)` value (never reused across runs)
- `DATABASE_URL` — the connection string built from your answers
- Any additional keys required by enabled features (MAIL_*, SENTRY_DSN, CORS_ORIGINS, etc.)

### Example session

```
╔══════════════════════════════════════════════════════════╗
║       Flask Boilerplate  ·  Project Setup Wizard        ║
╚══════════════════════════════════════════════════════════╝

  PROJECT  ─────────────────────────────────────────────

  Project name [my-app]: acme-api

  DATABASE  ────────────────────────────────────────────

  Select database backend:
    → [1] SQLite  (dev only, no server needed)
      [2] MySQL / MariaDB
      [3] PostgreSQL
      [4] No database  (disables auth)
  Choice [1]: 3

  Host [localhost]:
  Port [5432]:
  Database name [app]: acme
  User [app]: acme_user
  Password:

  FEATURES  ────────────────────────────────────────────

  Keep authentication system? [Y/n]: y
  Add Flask-Admin panel? [y/N]: n
  Add email support (Flask-Mail)? [y/N]: n
  Add rate limiting on auth routes (Flask-Limiter)? [y/N]: y
  Add CORS support (Flask-CORS)? [y/N]: n
  Add JSON API blueprint at /api/v1/? [y/N]: y
  Add security headers (Flask-Talisman)? [y/N]: y
  Add Sentry error tracking? [y/N]: n

  DEVOPS  ──────────────────────────────────────────────

  Keep Docker files? [Y/n]: y
  Generate GitHub Actions CI workflow? [y/N]: y
    Python version [3.12]:

  TESTING  ─────────────────────────────────────────────

  Keep test suite (pytest)? [Y/n]: y

  SUMMARY  ─────────────────────────────────────────────

  CONFIGURE    Rename project to "acme-api" in templates and README
  CONFIGURE    Set DATABASE_URL=postgresql+psycopg2://acme_user:***@localhost:5432/acme in .env
  KEEP         Authentication system (register, login, logout)
  ADD          Flask-Limiter to requirements.txt
  ADD          @limiter.limit("10 per minute") on /auth/login and /auth/register
  ADD          app/routes/api/v1/__init__.py  (Blueprint: api_v1_bp)
  ADD          app/routes/api/v1/users.py     (GET /api/v1/users stub)
  ADD          flask-talisman to requirements.txt
  KEEP         Dockerfile, docker-entrypoint.sh
  ADD          .github/workflows/test.yml  (Python 3.12, ruff + black + pytest)
  KEEP         tests/ directory and pytest configuration

  → Will generate .env with:
    SECRET_KEY   = <auto-generated secrets.token_hex(32)>
    DATABASE_URL = postgresql+psycopg2://acme_user:***@localhost:5432/acme

  Apply these changes? [Y/n]: y

  APPLYING  ────────────────────────────────────────────

  ✓ Project Name
  ✓ Database
  ✓ Authentication
  ✓ Rate Limiting
  ✓ JSON API Blueprint
  ✓ Security Headers
  ✓ Docker
  ✓ GitHub Actions CI
  ✓ Test Suite
  ✓ .env generated with a fresh SECRET_KEY

  DONE  ────────────────────────────────────────────────

  ✓ Project configured as "acme-api"
  → Backup saved to: .setup-backup/2026-04-13T19-32-00/
  → Next steps:
    1. Review .env and set any remaining values
    2. flask db migrate -m "initial schema"
    3. flask db upgrade
    4. flask run

  Remove setup/ directory and setup.py now? [y/N]:
```

---

## Configuration

### Environment classes

Configuration is class-based and selected via the `FLASK_ENV` environment variable.

| `FLASK_ENV` | Class | Key Differences |
|---|---|---|
| `development` | `DevelopmentConfig` | `DEBUG=True`, SQLite fallback, auto-creates tables, logs a warning if `SECRET_KEY` is not set |
| `testing` | `TestingConfig` | SQLite in-memory, CSRF disabled, logging suppressed |
| `production` | `ProductionConfig` | `SECURE` cookies, raises `RuntimeError` at boot if `SECRET_KEY` is missing |

All classes inherit from `Config`, which enforces `SESSION_COOKIE_HTTPONLY=True` and `SESSION_COOKIE_SAMESITE=Lax` in every environment. The `Secure` flag is only added in production.

### Environment variables reference

| Variable | Default | Required in Prod | Description |
|---|---|---|---|
| `SECRET_KEY` | `dev-key-change-me` | **Yes** | Flask session signing key. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | *(empty)* | No | SQLAlchemy connection URI. Omit to run without a database |
| `FLASK_ENV` | `development` | No | Selects config class: `development`, `testing`, or `production` |
| `LOG_LEVEL` | `INFO` (`DEBUG` in dev) | No | Python logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

---

## Routes

### Application routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/` | GET | — | Home page |
| `/about` | GET | — | About page |
| `/dashboard` | GET | Required | Protected page — redirects to login if unauthenticated |
| `/health` | GET | — | Health check endpoint |

### Auth routes

Registered only when `DB_ENABLED=True` (i.e., `DATABASE_URL` is set).

| Route | Method | Description |
|---|---|---|
| `/auth/register` | GET, POST | Create a new account |
| `/auth/login` | GET, POST | Sign in; supports `?next=` redirect |
| `/auth/logout` | POST | Sign out (POST-only to prevent CSRF via link) |

Use `@db_login_required` from `app/utils/decorators.py` instead of bare `@login_required` on routes that need to handle the no-database case gracefully (returns 503 instead of crashing).

---

## Health Check

`GET /health` — returns JSON with the overall status and, when a database is configured, the result of a live connectivity probe.

**Healthy (200):**
```json
{ "status": "ok", "db": "ok" }
```

**Unhealthy — DB unreachable (503):**
```json
{ "status": "unhealthy", "db": "unreachable" }
```

**No database configured (200):**
```json
{ "status": "ok" }
```

Use this endpoint for:
- Docker `HEALTHCHECK` (pre-configured in `Dockerfile`, polls every 30s)
- Kubernetes liveness and readiness probes
- Load balancer health checks
- Uptime monitoring services

---

## Database

The database layer is **optional**. If `DATABASE_URL` is not set, the ORM, migrations, and auth blueprint are never loaded — the app runs as a lightweight template server.

### Connection strings

**SQLite** (no server required — development only):
```env
DATABASE_URL=sqlite:///instance/dev.db
```

**MySQL / MariaDB:**
```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname?charset=utf8mb4
```

**PostgreSQL:**
```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dbname
```

### Migrations

The `migrations/` directory is pre-initialized. To create and apply a migration after changing a model:

```bash
flask db migrate -m "describe your change"
flask db upgrade
```

To roll back:
```bash
flask db downgrade
```

> **Docker:** `flask db upgrade` runs automatically on container startup via `docker-entrypoint.sh`. No manual step needed in containerized environments.

In development, tables are also created automatically on first boot (`AUTO_CREATE_TABLES=True`), so you can start without running migrations.

---

## Security

### SECRET_KEY

- In **development**, the app starts with an insecure fallback key and logs a `WARNING`. This is intentional — it lets you boot without configuration.
- In **production**, `ProductionConfig.init_app()` raises a `RuntimeError` at startup if `SECRET_KEY` is not set. The server will refuse to start rather than run with a weak key.

Generate a strong key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Session and cookie hardening

| Setting | Development | Production |
|---|---|---|
| `SESSION_COOKIE_HTTPONLY` | True | True |
| `SESSION_COOKIE_SAMESITE` | Lax | Lax |
| `SESSION_COOKIE_SECURE` | False | True |
| `REMEMBER_COOKIE_HTTPONLY` | True | True |
| `REMEMBER_COOKIE_SECURE` | False | True |

### CSRF

All state-changing requests (POST/PUT/DELETE) are protected by Flask-WTF's `CSRFProtect`. The logout route uses `POST` to prevent CSRF-driven logout via a crafted link. CSRF is only disabled in `TestingConfig`.

### Password storage

Passwords are hashed with `werkzeug.security.generate_password_hash` (PBKDF2-HMAC-SHA256). Plain-text passwords are never stored or logged.

### Open-redirect guard

The `/auth/login?next=` redirect validates that `next` is a relative URL (`urlsplit(next).netloc == ""`), preventing redirect to external domains.

---

## Logging

Logging is configured in `app/utils/logger.py` and registered during `create_app()`. It is suppressed during testing.

- **File handler** — `logs/app.log`, rotating at 10 MB with 5 backups kept
- **Stream handler** — stdout/stderr (captured by Gunicorn and Docker)
- **Format** — includes timestamp, level, logger name, request ID, message, and source location

Every log line includes a `request_id` field that uniquely identifies the request. The ID is either:
- Generated as `uuid4().hex` for new requests
- Echoed from the `X-Request-ID` header if sent by a reverse proxy (e.g., nginx, AWS ALB)

The same ID is also returned in the `X-Request-ID` response header, enabling end-to-end tracing across services.

---

## Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Single module, verbose
pytest tests/test_auth.py -v
```

Tests use an in-memory SQLite database, have CSRF disabled, and set `FLASK_ENV=testing` automatically via `pytest-env`.

### Available fixtures

| Fixture | Scope | Description |
|---|---|---|
| `app` | session | App instance with tables created; torn down after the session |
| `db` | function | Yields the DB; truncates all rows after each test |
| `client` | function | Unauthenticated Flask test client |
| `runner` | function | Flask CLI test runner |
| `auth_client` | function | Test client pre-logged in as `testuser` |

---

## Docker

```bash
# Build
docker build -t my-app .

# Run
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db \
  -e FLASK_ENV=production \
  my-app
```

### What happens on startup

1. If `DATABASE_URL` is set, `flask db upgrade` runs automatically before the server starts
2. Gunicorn starts with graceful shutdown support (`--graceful-timeout 30`)
3. Docker's built-in `HEALTHCHECK` polls `/health` every 30 seconds

### Optional environment variables

| Variable | Default | Description |
|---|---|---|
| `GUNICORN_WORKERS` | `4` | Number of Gunicorn worker processes |
| `PORT` | `8000` | Port the server listens on |
| `GUNICORN_TIMEOUT` | `120` | Worker timeout in seconds |

The container runs as a non-root user (`app:app`). Logs go to stdout/stderr and are captured by the container runtime.

---

## Development Tools

```bash
# Format
black .

# Lint
ruff check .

# Lint with auto-fix
ruff check . --fix

# Type check
mypy app/
```

Configuration for Black, Ruff, and mypy is in `pyproject.toml` (100-character line length, Python 3.11+ target).

---

## Adding Features

See [docs/add-feature.md](docs/add-feature.md) for a step-by-step guide on adding new blueprints, models, forms, templates, and tests following this project's conventions.

Other references:
- [docs/project-overview.md](docs/project-overview.md) — architecture decisions and initialization order
- [docs/database.md](docs/database.md) — models, migrations, and backend-specific behavior
- [docs/auth-and-security.md](docs/auth-and-security.md) — auth flow, CSRF, and cookie security

---

## Contributing

1. Fork the repository and create a branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run the full quality check before opening a PR:
   ```bash
   ruff check . && black --check . && pytest
   ```
4. Commit following [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
5. Push and open a pull request against `main`

---

## License

MIT
