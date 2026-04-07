# Database

---

## Backend Support

Three backends are supported. Selection is automatic based on the `DATABASE_URL` scheme.

| Scheme | Driver | Notes |
|---|---|---|
| `sqlite:///` | built-in | Dev default, in-memory for tests |
| `mysql+pymysql://` | PyMySQL | `charset=utf8mb4` required in URL |
| `postgresql+psycopg2://` | psycopg2-binary | Explicit dialect required in SQLAlchemy 2 |

**URL formats:**
```
# SQLite
sqlite:///instance/dev.db
sqlite:///:memory:

# MySQL
mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4

# PostgreSQL
postgresql+psycopg2://user:pass@host:5432/db
```

`_engine_options(uri)` in `config.py` is the single place that maps URI schemes to connection pool settings. When adding a new backend, add detection there.

---

## Development vs Production Table Management

**Development** (`AUTO_CREATE_TABLES=True`): `db.create_all()` runs automatically in `create_app()`. Creates tables that don't exist and skips existing ones. Does not handle column changes.

**Production** (`AUTO_CREATE_TABLES=False`): tables are managed exclusively via Flask-Migrate.

```bash
flask db init                        # once — generates migrations/
flask db migrate -m "describe change"
flask db upgrade                     # apply pending migrations
flask db downgrade                   # roll back one revision
```

Always review auto-generated migrations before applying. Alembic cannot detect renamed columns, type changes on SQLite, or some index changes. Every `upgrade()` must have a working `downgrade()`.

---

## Model Conventions

Reference: `app/models/user.py`

**Timestamp columns:**
```python
from datetime import datetime, timezone

created_at = db.Column(
    db.DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    nullable=False,
)
updated_at = db.Column(
    db.DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
    nullable=False,
)
```

`lambda:` is required. A bare `datetime.now` is evaluated once at class definition time, not at insert time.

**Query style (SQLAlchemy 2.0):**
```python
# Fetch by primary key
obj = db.session.get(Model, pk)

# Filter
obj = Model.query.filter_by(email=email).first()

# Prefer select() for new code
from sqlalchemy import select
stmt = select(Model).where(Model.email == email)
obj = db.session.scalar(stmt)
```

Never use `text()` with string interpolation for user input. Use ORM or bound parameters.

---

## Session Management

Flask-SQLAlchemy scopes the session to the request. Do not manually manage `db.session` beyond the basics:

```python
db.session.add(obj)
db.session.commit()

db.session.delete(obj)
db.session.commit()
```

The 500 error handler in `app/errors/handlers.py` calls `db.session.rollback()` automatically. Do not call `db.session.close()` manually.

---

## Testing

Tests use `TestingConfig` with SQLite in-memory (`sqlite:///:memory:`). Tables are created once per session and rows are cleared after each test by the `db` fixture.

The `db` fixture clears rows in reverse FK order:
```python
for table in reversed(_db.metadata.sorted_tables):
    _db.session.execute(table.delete())
_db.session.commit()
```

Never target the development or production database in tests. `TestingConfig` hardcodes the in-memory URI with no override path.

---

## Common Mistakes

| Mistake | Correct |
|---|---|
| `default=datetime.now(timezone.utc)` | `default=lambda: datetime.now(timezone.utc)` |
| `Model.query.get(id)` | `db.session.get(Model, id)` |
| Model imported at top of forms file | Imported inside `validate_*` method |
| `db.create_all()` in production | `flask db upgrade` |
| `text("... WHERE id = " + str(id))` | `db.session.get(Model, id)` |
| `db.session.close()` called manually | Let Flask-SQLAlchemy handle teardown |
