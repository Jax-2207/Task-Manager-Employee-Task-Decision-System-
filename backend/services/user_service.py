"""User service — business logic for user registration and lookup."""

from exceptions import NotFoundError, ValidationError
from models.user import UserRole
from repositories import user_repository


def register_employee(firebase_uid, email):
    """Register a new employee via Google Sign-In.

    Raises:
        ValidationError: If user with this firebase_uid already exists.
    """
    existing = user_repository.get_by_firebase_uid(firebase_uid)
    if existing:
        raise ValidationError("User already registered")

    return user_repository.create(
        firebase_uid=firebase_uid,
        email=email,
        role=UserRole.EMPLOYEE,
    )


def get_or_create_admin(email):
    """Get or create the admin user in the local database.

    Admin doesn't use Firebase, so firebase_uid is set to 'admin-local'.
    """
    user = user_repository.get_by_firebase_uid("admin-local")
    if user:
        return user

    return user_repository.create(
        firebase_uid="admin-local",
        email=email,
        role=UserRole.ADMIN,
    )


def get_admin_user():
    """Return the admin user, or None."""
    return user_repository.get_by_firebase_uid("admin-local")


def get_user_by_firebase_uid(firebase_uid):
    """Look up a user by Firebase UID. Raises NotFoundError if missing."""
    user = user_repository.get_by_firebase_uid(firebase_uid)
    if user is None:
        raise NotFoundError("User", firebase_uid)
    return user


def get_user_by_employee_id(employee_id):
    """Look up a user by their employee_id string. Raises NotFoundError if missing."""
    user = user_repository.get_by_employee_id(employee_id)
    if user is None:
        raise NotFoundError("Employee", employee_id)
    return user
