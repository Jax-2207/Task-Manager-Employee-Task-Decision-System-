"""Authentication middleware — decorators for route-level auth and role checks."""

import functools
import logging

from flask import g, request

from exceptions import UnauthorizedError, ForbiddenError
from firebase_config import verify_firebase_token
from repositories import user_repository

logger = logging.getLogger(__name__)


def require_auth(f):
    """Decorator: verify token and attach user to g.user.

    Accepts either:
    - Admin session token (from hardcoded login)
    - Firebase ID token (from Google Sign-In)

    Expects header: Authorization: Bearer <token>
    """

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise UnauthorizedError("Missing or invalid Authorization header")

        token = auth_header.split("Bearer ", 1)[1]

        # Check if admin session token
        from routes.auth_routes import is_admin_token
        if is_admin_token(token):
            from services.user_service import get_admin_user
            user = get_admin_user()
            if user is None:
                raise UnauthorizedError("Admin user not found")
            g.user = user
            return f(*args, **kwargs)

        # Otherwise, verify as Firebase token (Google Sign-In)
        try:
            decoded = verify_firebase_token(token)
        except ValueError as e:
            raise UnauthorizedError(str(e))

        firebase_uid = decoded["uid"]
        user = user_repository.get_by_firebase_uid(firebase_uid)
        if user is None:
            raise UnauthorizedError("User not registered. Please sign in with Google first.")

        g.user = user
        return f(*args, **kwargs)

    return decorated


def require_admin(f):
    """Decorator: require_auth + check that user role is ADMIN."""

    @functools.wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        if g.user.role.value != "ADMIN":
            raise ForbiddenError("Admin access required")
        return f(*args, **kwargs)

    return decorated
