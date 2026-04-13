# Flask Boilerplate

A production-ready Flask starter with authentication, multi-database support, migrations, structured logging, and a full test suite — ready to clone and build on.

---

## Features

- **Application Factory** pattern with environment-based configuration
- **Optional database** — the app boots and runs without any DB configured
- **Multi-backend** — SQLite, MySQL, and PostgreSQL supported out of the box
- **Authentication** — register, login, logout via Flask-Login with secure session cookies
- **CSRF protection** on all forms via Flask-WTF
- **Migrations** with Flask-Migrate (Alembic) — directory pre-initialized, runs automatically on Docker startup
- **Health check** endpoint at `/health` with optional database connectivity check
- **Request ID** injected into every log line for distributed tracing
- **Structured logging** with rotating file handler + stdout
- **Error pages** for 403, 404, and 500 with automatic session rollback
- **Tailwind CSS** via CDN, no build step required
- **Docker** ready with non-root user, automatic migrations, HEALTHCHECK, and graceful shutdown

---

## Tech Stack

| Layer | Library |
|---|---|
| Web framework | Flask 3 |
| ORM | SQLAlchemy 2 + Flask-SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Auth | Flask-Login |
| Forms & CSRF | Flask-WTF + WTForms |
| MySQL driver | PyMySQL |
| PostgreSQL driver | psycopg2-binary |
| Password hashing | Werkzeug |
| WSGI server | Gunicorn |
| CSS | Tailwind CSS (CDN) |
| Testing | pytest + pytest-flask |

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
│   │   ├── decorators.py        # db_login_required
│   │   ├── logger.py            # RotatingFileHandler + request ID filter
│   │   └── middleware.py        # before/after request hooks (timing, request ID)
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
├── tests/
│   ├── conftest.py              # Fixtures: app, db, client, runner, auth_client
│   ├── test_auth.py             # Auth flow tests
│   └── test_main.py             # Route tests
├── docs/
│   ├── project-overview.md      # Architecture decisions and conventions
│   ├── add-feature.md           # How to add a new feature module
│   ├── database.md              # Database guide (models, migrations, backends)
│   └── auth-and-security.md    # Auth and security patterns
├── config.py                    # Config classes (Development, Testing, Production)
├── run.py                       # Dev entry point (respects FLASK_ENV)
├── wsgi.py                      # Production entry point (gunicorn)
├── Dockerfile
├── docker-entrypoint.sh         # Runs migrations then starts gunicorn
├── .env.example
├── .flaskenv
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

---

## Getting Started

### 1. Clone the repository

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

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```env
SECRET_KEY=        # generate one: python -c "import secrets; print(secrets.token_hex(32))"
DATABASE_URL=      # see Database section below
```

> **Note:** In development, if `SECRET_KEY` is not set, the app boots with an insecure default key and logs a warning. In production, startup fails immediately with an error if `SECRET_KEY` is missing.

### 5. Run the development server

```bash
flask run
```

Visit `http://localhost:5000`.

---

## Database

The database is **optional**. If `DATABASE_URL` is not set, the app runs without auth routes. Set it to enable authentication and the dashboard.

### SQLite (no setup required)

```env
DATABASE_URL=sqlite:///instance/dev.db
```

In development, tables are created automatically on first boot (`AUTO_CREATE_TABLES=True`).

### MySQL

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname?charset=utf8mb4
```

### PostgreSQL

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dbname
```

### Migrations

The `migrations/` directory is already initialized. To create and apply a new migration:

```bash
flask db migrate -m "describe your change"
flask db upgrade
```

> **Docker:** Migrations run automatically on container startup via `docker-entrypoint.sh`. No manual step needed.

---

## Configuration

Configuration is class-based and selected via the `FLASK_ENV` environment variable.

| `FLASK_ENV` | Class | Key Differences |
|---|---|---|
| `development` | `DevelopmentConfig` | `DEBUG=True`, SQLite fallback, auto-creates tables, warns if `SECRET_KEY` not set |
| `testing` | `TestingConfig` | SQLite in-memory, CSRF disabled, logging suppressed |
| `production` | `ProductionConfig` | `SECURE` cookies, raises `RuntimeError` at boot if `SECRET_KEY` missing |

All classes inherit from `Config` which sets secure cookie defaults (`HttpOnly`, `SameSite=Lax`) for every environment. `Secure` is only enabled in production.

---

## Routes

### Application routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Home page |
| `/about` | GET | About page |
| `/dashboard` | GET | Protected — requires login |
| `/health` | GET | Health check (see below) |

### Auth routes

| Route | Method | Description |
|---|---|---|
| `/auth/register` | GET, POST | Create a new account |
| `/auth/login` | GET, POST | Sign in, supports `?next=` redirect |
| `/auth/logout` | POST | Sign out (POST-only to prevent CSRF via link) |

Auth routes are only registered when `DB_ENABLED=True`. Use `@db_login_required` (from `app/utils/decorators.py`) instead of bare `@login_required` on routes that should handle the no-database case gracefully.

---

## Health Check

`GET /health` — returns JSON with the overall status and, when a database is configured, the result of a connectivity probe.

**Healthy (200):**
```json
{ "status": "ok", "db": "ok" }
```

**Unhealthy — DB unreachable (503):**
```json
{ "status": "unhealthy", "db": "unreachable" }
```

When `DATABASE_URL` is not set, the response is simply `{ "status": "ok" }` (no `db` key).

Use this endpoint for:
- Docker `HEALTHCHECK` (already configured in `Dockerfile`)
- Kubernetes liveness and readiness probes
- Load balancer health checks
- Uptime monitoring

---

## Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing
```

Tests use an in-memory SQLite database and have CSRF disabled. Available fixtures:

| Fixture | Scope | Description |
|---|---|---|
| `app` | session | App instance with tables created |
| `db` | function | Clears all rows after each test |
| `client` | function | Unauthenticated HTTP client |
| `runner` | function | CLI test runner |
| `auth_client` | function | HTTP client pre-logged in as `testuser` |

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

The container runs as a non-root user. Logs go to stdout/stderr.

---

## Development Tools

```bash
# Format
black .

# Lint
ruff check .

# Type check
mypy app/
```

Configuration for all three is in `pyproject.toml` (100-char line length, Python 3.11+).

---

## Adding Features

See [docs/add-feature.md](docs/add-feature.md) for a step-by-step guide on adding new blueprints, models, forms, templates, and tests following this project's conventions.

Other references:
- [docs/project-overview.md](docs/project-overview.md) — architecture decisions and initialization order
- [docs/database.md](docs/database.md) — models, migrations, and backend-specific behavior
- [docs/auth-and-security.md](docs/auth-and-security.md) — auth flow, CSRF, cookie security

---

## Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to your fork: `git push origin feature/your-feature`
5. Open a pull request

---

## License

MIT
