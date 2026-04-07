# Project Overview

Production-ready Flask 3 boilerplate using the Application Factory pattern. The database is **optional** — the app boots and serves routes without any database configured. Auth features activate only when `DB_ENABLED=True`.

---

## Directory Map

```
app/
├── __init__.py          # create_app() — single entry point
├── extensions.py        # db, migrate, login_manager, csrf — instantiated without app context
├── models/user.py       # Only model. user_loader registered here.
├── forms/auth_forms.py  # LoginForm, RegisterForm with lazy DB imports
├── routes/
│   ├── main.py          # main_bp: /, /dashboard, /about
│   └── auth.py          # auth_bp: /auth/register, /auth/login, /auth/logout
├── errors/handlers.py   # 403, 404, 500 via app_errorhandler (global scope)
└── utils/
    ├── decorators.py    # db_login_required — checks DB_ENABLED then login
    ├── logger.py        # RotatingFileHandler + RequestIdFilter
    └── middleware.py    # before_request/after_request: request ID + timing

config.py                # Config hierarchy + _engine_options() per backend
run.py                   # Dev entry: create_app("development")
wsgi.py                  # Prod entry: create_app(FLASK_ENV or "production")
```

---

## create_app() Initialization Order

This order is load-bearing. Do not reorder.

1. Load config object
2. `config[name].init_app(app)` — validates env vars in production
3. `_register_extensions()` — csrf and login_manager always; db+migrate only if `DB_ENABLED`
4. `_register_blueprints()` — main_bp always; auth_bp only if `DB_ENABLED`
5. `_register_error_handlers()` — errors_bp always
6. `_configure_logging()` — skipped in testing
7. `_register_middleware()` — before/after request hooks
8. `db.create_all()` — only if `DB_ENABLED and AUTO_CREATE_TABLES`

---

## DB_ENABLED Flag

`DB_ENABLED` is computed at class definition time from `DATABASE_URL` presence. It is static after `create_app()` runs.

| `DATABASE_URL` | Environment | `DB_ENABLED` | Effect |
|---|---|---|---|
| absent | production | `False` | App boots, no auth routes |
| `sqlite:///instance/dev.db` | development | `True` | SQLite fallback (default) |
| `sqlite:///:memory:` | testing | `True` | In-memory, isolated |
| `mysql+pymysql://...` | any | `True` | Full MySQL |
| `postgresql+psycopg2://...` | any | `True` | Full PostgreSQL |

When `DB_ENABLED=False`:
- `auth_bp` is not registered → `/auth/*` routes do not exist
- `login_manager.login_view` is set to `None` → no redirect loop
- `/dashboard` returns 503 via `db_login_required`
- Navbar auth links hidden via `{% if config.DB_ENABLED %}`

---

## Configuration Classes

```
Config (base)
├── DevelopmentConfig   DEBUG=True, AUTO_CREATE_TABLES=True, SQLite default
├── TestingConfig       TESTING=True, SQLite :memory:, CSRF disabled
└── ProductionConfig    SESSION_COOKIE_SECURE=True, SECRET_KEY required
```

Cookie security is split intentionally:
- `HTTPONLY=True` and `SAMESITE="Lax"` → base class (safe everywhere)
- `SECURE=True` → production only (localhost has no HTTPS)

---

## Engine Options Per Backend

`_engine_options(uri)` in `config.py` returns different dicts per backend:

- **SQLite**: `connect_args={"check_same_thread": False}` — required for multi-worker gunicorn
- **MySQL**: `pool_pre_ping=True, pool_recycle=300` — combats `wait_timeout` disconnects
- **PostgreSQL**: same + `pool_size=5, max_overflow=10` — explicit pool sizing

---

## Key Conventions

- Never import models at module top level — always inside functions to avoid circular imports
- `url_for()` everywhere — zero hardcoded URLs in Python or templates
- Flash categories: `success`, `danger`, `warning`, `info` — match CSS classes in `style.css`
- Logout is POST-only — form with CSRF token in `base.html`, never a GET link
- `next` param on login validates with `urlsplit().netloc != ""` to prevent open redirect
- Timestamps use `lambda: datetime.now(timezone.utc)` — timezone-aware, always UTC
- `db.session.get(Model, pk)` — SQLAlchemy 2.0 style, not `.query.get()`

---

## Logging Format

```
2026-04-07 12:00:00 INFO [app] [a3f1c9d2] GET /dashboard 200 4.21ms [in app/routes/main.py:14]
```

`request_id` is injected by `_RequestIdFilter` — reads from `g.request_id` when inside a request context, `-` otherwise. All `app.logger.*` calls automatically include it without any extra arguments.

---

## Testing Fixtures

| Fixture | Scope | Purpose |
|---|---|---|
| `app` | session | Single app instance, creates/drops tables once |
| `db` | function | Clears all rows after each test in FK-safe order |
| `client` | function | HTTP test client |
| `runner` | function | CLI test runner |
| `auth_client` | function | Pre-logged-in client with `testuser` / `test@example.com` |

`TestingConfig` disables CSRF so forms can be submitted without tokens in tests.
