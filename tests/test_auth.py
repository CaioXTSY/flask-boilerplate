from __future__ import annotations

from app.extensions import db as _db
from app.models.user import User


def _register(client, username="newuser", email="new@example.com", password="password123"):
    return client.post(
        "/auth/register",
        data={"username": username, "email": email, "password": password, "password2": password},
        follow_redirects=True,
    )


def _login(client, email="test@example.com", password="password123"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def _logout(client):
    return client.post("/auth/logout", follow_redirects=True)


def test_register_success(client, db):
    response = _register(client)
    assert response.status_code == 200
    assert b"Account created" in response.data
    assert User.query.filter_by(email="new@example.com").first() is not None


def test_register_duplicate_email(client, db):
    _register(client)
    response = _register(client, username="anotheruser")
    assert b"already registered" in response.data


def test_register_duplicate_username(client, db):
    _register(client)
    response = _register(client, email="other@example.com")
    assert b"already taken" in response.data


def test_login_success(client, db):
    user = User(username="loginuser", email="login@example.com")
    user.set_password("password123")
    _db.session.add(user)
    _db.session.commit()

    response = _login(client, email="login@example.com")
    assert response.status_code == 200


def test_login_wrong_password(client, db):
    user = User(username="wrongpass", email="wrongpass@example.com")
    user.set_password("correct123")
    _db.session.add(user)
    _db.session.commit()

    response = _login(client, email="wrongpass@example.com", password="wrongpassword")
    assert b"Invalid email or password" in response.data


def test_login_nonexistent_user(client, db):
    response = _login(client, email="noone@example.com")
    assert b"Invalid email or password" in response.data


def test_logout(auth_client):
    response = _logout(auth_client)
    assert response.status_code == 200
    assert b"Signed out" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302


def test_dashboard_authenticated(auth_client):
    response = auth_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data
