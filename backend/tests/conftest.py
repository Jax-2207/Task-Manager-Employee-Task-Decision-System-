"""Pytest fixtures for Decision Management System tests."""

import sys
import os
import pytest

# Ensure the backend root is on sys.path so imports resolve correctly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from config import TestConfig
from models import db as _db
from models.user import UserRole
from repositories import user_repository


@pytest.fixture(scope="function")
def app():
    """Create a Flask app configured for testing (in-memory SQLite)."""
    app = create_app(config_class=TestConfig)
    yield app


@pytest.fixture(scope="function")
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def db(app):
    """Set up and tear down the database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


def _create_admin(app):
    """Helper: create an admin user inside app context. Returns (id, employee_id, email)."""
    user = user_repository.create(
        firebase_uid="admin-uid-001",
        email="admin@test.com",
        role=UserRole.ADMIN,
    )
    return {"id": user.id, "employee_id": user.employee_id, "email": user.email}


def _create_employee(app, suffix="001"):
    """Helper: create an employee user inside app context. Returns dict with user info."""
    user = user_repository.create(
        firebase_uid=f"employee-uid-{suffix}",
        email=f"employee{suffix}@test.com",
        role=UserRole.EMPLOYEE,
    )
    return {"id": user.id, "employee_id": user.employee_id, "email": user.email}


@pytest.fixture(scope="function")
def admin_user(app):
    """Return dict with admin user info. Must be used inside app.app_context()."""
    with app.app_context():
        return _create_admin(app)


@pytest.fixture(scope="function")
def employee_user(app):
    """Return dict with employee user info. Must be used inside app.app_context()."""
    with app.app_context():
        return _create_employee(app, "001")


@pytest.fixture(scope="function")
def employee_user_2(app):
    """Return dict with second employee user info."""
    with app.app_context():
        return _create_employee(app, "002")
