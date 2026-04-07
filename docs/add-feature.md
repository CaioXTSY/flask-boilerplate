# Adding a New Feature

A feature in this project is a vertical slice: model → blueprint → forms → templates → tests. All layers are expected for any feature that persists data or accepts user input.

---

## Step 1 — Model

Create `app/models/<name>.py`. Follow `app/models/user.py` as the canonical reference.

```python
from __future__ import annotations
from datetime import datetime, timezone
from app.extensions import db

class Thing(db.Model):
    __tablename__ = "things"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
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

Always use `lambda:` for `default` and `onupdate` — a bare `datetime.now` is evaluated once at import time, not at insert time.

After creating the model:

1. Export from `app/models/__init__.py`:
```python
from app.models.thing import Thing
__all__ = ["User", "Thing"]
```

2. Add to `make_shell_context()` in `app/__init__.py`:
```python
from app.models.thing import Thing
ctx.update({"Thing": Thing})
```

---

## Step 2 — Blueprint

Create `app/routes/<name>.py`:

```python
from __future__ import annotations
from flask import Blueprint, render_template, flash, redirect, url_for
from app.utils.decorators import db_login_required

thing_bp = Blueprint("thing", __name__)

@thing_bp.route("/things")
def index():
    return render_template("things/index.html")

@thing_bp.route("/things/<int:id>")
@db_login_required
def detail(id: int):
    from app.models.thing import Thing
    thing = db.session.get(Thing, id)
    ...
```

Import models inside view functions, not at the top of the file — this avoids circular imports.

Register in `app/__init__.py` inside `_register_blueprints()`. If the blueprint requires a database, wrap it:

```python
if app.config.get("DB_ENABLED"):
    from app.routes.thing import thing_bp
    app.register_blueprint(thing_bp, url_prefix="/things")
```

---

## Step 3 — Forms

Add to `app/forms/` and export from `app/forms/__init__.py`.

```python
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class ThingForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Save")
```

Custom validators that query the database must use lazy imports:

```python
def validate_title(self, field):
    from app.models.thing import Thing
    if Thing.query.filter_by(title=field.data).first():
        raise ValidationError("This title is already taken.")
```

---

## Step 4 — Templates

Create `app/templates/<feature>/` and extend `base.html`:

```html
{% extends "base.html" %}

{% block title %}Things — Meu App{% endblock %}

{% block content %}
<section>
  <h1>Things</h1>
  <form method="post" action="{{ url_for('thing.create') }}" novalidate>
    {{ form.hidden_tag() }}

    <div class="form-group">
      {{ form.title.label }}
      {{ form.title(class="form-control") }}
      {% for error in form.title.errors %}
        <span class="form-error">{{ error }}</span>
      {% endfor %}
    </div>

    {{ form.submit(class="btn btn-primary") }}
  </form>
</section>
{% endblock %}
```

Every form must include `{{ form.hidden_tag() }}` — this provides the CSRF token. Use `url_for()` in all `action=` and `href=` attributes. Flash messages are already rendered in `base.html`.

Available CSS classes: `btn`, `btn-primary`, `btn-secondary`, `form-group`, `form-control`, `form-error`, `alert-success`, `alert-danger`, `alert-warning`, `alert-info`.

---

## Step 5 — Tests

Create `tests/test_<feature>.py`:

```python
from app.models.thing import Thing

def test_index_ok(client):
    response = client.get("/things")
    assert response.status_code == 200

def test_create_success(client, db):
    response = client.post(
        "/things/create",
        data={"title": "My Thing"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert Thing.query.filter_by(title="My Thing").first() is not None

def test_create_invalid(client, db):
    response = client.post("/things/create", data={}, follow_redirects=True)
    assert response.status_code == 200  # re-renders form with errors

def test_protected_requires_login(client):
    response = client.get("/things/1", follow_redirects=False)
    assert response.status_code == 302  # redirected to login
```

Use `client` for anonymous requests, `auth_client` for authenticated ones, `db` when the test writes to the database. CSRF is disabled in `TestingConfig` — POST directly without tokens.

---

## Checklist

- [ ] Model has `__tablename__` and all required columns with `nullable=False`
- [ ] Timestamps use `lambda: datetime.now(timezone.utc)`
- [ ] Model exported from `app/models/__init__.py`
- [ ] Model added to `make_shell_context()` in `app/__init__.py`
- [ ] Blueprint registered in `_register_blueprints()`, conditionally if DB-dependent
- [ ] All forms include `{{ form.hidden_tag() }}`
- [ ] All redirects and links use `url_for()`, no hardcoded paths
- [ ] Protected routes use `@db_login_required`
- [ ] At least one test per route (happy path + error case)
- [ ] Flash messages use correct categories: `success`, `danger`, `warning`, `info`
