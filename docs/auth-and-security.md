# Auth and Security

---

## Stack

| Concern | Library | File |
|---|---|---|
| Session management | Flask-Login | `app/extensions.py`, `app/models/user.py` |
| CSRF protection | Flask-WTF | `app/extensions.py`, all forms |
| Password hashing | Werkzeug | `app/models/user.py` |
| Form validation | WTForms | `app/forms/auth_forms.py` |
| Cookie security | Flask config | `config.py` |
| Open redirect prevention | stdlib `urlsplit` | `app/routes/auth.py` |

Auth is only active when `DB_ENABLED=True`. When the database is absent, `auth_bp` is not registered and no auth routes exist.

---

## Flask-Login

`login_manager` is initialized in `_register_extensions()`. Its `login_view` is set conditionally:

```python
if app.config.get("DB_ENABLED"):
    login_manager.login_view = "auth.login"
else:
    login_manager.login_view = None  # prevents BuildError when blueprint is absent
```

The `user_loader` lives in `app/models/user.py`:

```python
@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))
```

It runs on every request that accesses `current_user`. Keep it a single DB lookup with no joins.

---

## Protected Routes

Use `@db_login_required` from `app.utils.decorators` on any route that might run when the database is absent:

```python
from app.utils.decorators import db_login_required

@main_bp.route("/dashboard")
@db_login_required
def dashboard():
    ...
```

Behavior:
1. `DB_ENABLED=False` → `abort(503)`
2. User not authenticated → redirect to `auth.login`
3. Authenticated → execute view

Bare `@login_required` is acceptable inside blueprints that only register when `DB_ENABLED=True` (such as `auth_bp` itself).

---

## Login Flow

`GET/POST /auth/login` — `app/routes/auth.py`:

1. Already authenticated → redirect to `/`
2. Validate `LoginForm` on POST
3. Fetch user by email
4. `user.check_password(form.password.data)`
5. Invalid → flash danger and redirect back (do not reveal which field failed)
6. `login_user(user, remember=form.remember_me.data)`
7. Validate `next` and redirect

**Open redirect prevention:**
```python
next_page = request.args.get("next")
if next_page:
    parsed = urlsplit(next_page)
    if parsed.netloc != "":   # external domain — reject
        next_page = None
redirect(next_page or url_for("main.index"))
```

Never skip this check. Any `next` value with a netloc is an open redirect vector.

---

## Logout

POST-only. In `base.html`, logout is a form, not a link:

```html
<form action="{{ url_for('auth.logout') }}" method="post" style="display:inline;">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
    <button type="submit" class="btn-link">Sair</button>
</form>
```

The CSRF token is injected manually here (no WTForm object available in the base template). This is correct and intentional.

---

## Password Handling

`User.set_password()` hashes via `werkzeug.security.generate_password_hash()` (PBKDF2-HMAC-SHA256). `User.check_password()` uses constant-time comparison via `check_password_hash()`.

```python
user = User(username=..., email=...)
user.set_password(form.password.data)
db.session.add(user)
db.session.commit()
```

Never store or log plain-text passwords. The `password_hash` field has no serializer or property getter by design.

---

## CSRF

`CSRFProtect` is initialized globally — all POST/PUT/PATCH/DELETE requests are protected automatically.

- **WTForms**: use `{{ form.hidden_tag() }}` in every form
- **Non-WTForm POST** (e.g., logout in base template): inject manually with `{{ csrf_token() }}`
- **Tests**: `TestingConfig` sets `WTF_CSRF_ENABLED=False` — never disable in non-test code

---

## Cookie Security

Split between base and production classes intentionally:

**`Config` (all environments):**
```python
SESSION_COOKIE_HTTPONLY = True     # JS cannot read session cookie — XSS mitigation
SESSION_COOKIE_SAMESITE = "Lax"   # not sent on cross-site POST — CSRF mitigation
REMEMBER_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_SAMESITE = "Lax"
```

**`ProductionConfig` only:**
```python
SESSION_COOKIE_SECURE = True       # cookie only sent over HTTPS
REMEMBER_COOKIE_SECURE = True
```

**`DevelopmentConfig` / `TestingConfig`:**
```python
SESSION_COOKIE_SECURE = False      # localhost has no HTTPS; True silently breaks login
REMEMBER_COOKIE_SECURE = False
```

---

## Form Validators

Custom validators in `RegisterForm` prevent duplicate usernames and emails. They use lazy imports to avoid circular dependencies:

```python
def validate_email(self, field):
    from app.models.user import User    # import inside method — required
    if User.query.filter_by(email=field.data).first():
        raise ValidationError("Este e-mail já está cadastrado.")
```

WTForms calls `validate_<fieldname>()` automatically after built-in validators pass. Do not move model imports to the top of the forms file.

---

## Checklist

- [ ] New POST routes protected by CSRF (automatic via global `CSRFProtect`)
- [ ] Passwords stored only via `user.set_password()`, never plain
- [ ] `next` param validated before any redirect in login flows
- [ ] Logout is POST, not GET
- [ ] Protected routes use `@db_login_required`
- [ ] No secrets in source code — all via env vars
- [ ] `SECRET_KEY` validated at boot in `ProductionConfig.init_app()`
- [ ] `SESSION_COOKIE_SECURE=True` confirmed for production deployments
