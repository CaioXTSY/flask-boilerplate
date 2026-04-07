from __future__ import annotations

import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.remove()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def auth_client(client, db):
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    _db.session.add(user)
    _db.session.commit()

    client.post(
        "/auth/login",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=True,
    )
    return client
