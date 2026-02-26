"""Auth routes — handles admin login, employee registration via Google, and profile."""

import logging
import os
import secrets

from flask import Blueprint, jsonify, request

from firebase_config import verify_firebase_token
from exceptions import UnauthorizedError, ValidationError
from services import user_service

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# --- Hardcoded admin credentials ---
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@gmail.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin@1234")

# Simple token store for admin sessions (in-memory, resets on server restart)
_admin_tokens = set()


def is_admin_token(token):
    """Check if a token is a valid admin session token."""
    return token in _admin_tokens


@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """POST /api/auth/admin/login — admin signs in with hardcoded credentials.

    Expects JSON: { "email": "...", "password": "..." }
    Returns a session token.
    """
    json_data = request.get_json(silent=True) or {}
    email = json_data.get("email", "").strip()
    password = json_data.get("password", "")

    if email.lower() != ADMIN_EMAIL.lower() or password != ADMIN_PASSWORD:
        raise UnauthorizedError("Invalid admin credentials")

    # Generate a simple session token
    token = secrets.token_urlsafe(48)
    _admin_tokens.add(token)

    # Get or create the admin user in DB
    user = user_service.get_or_create_admin(email)

    return jsonify({
        "token": token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/google/register", methods=["POST"])
def google_register():
    """POST /api/auth/google/register — employee signs in with Google.

    Expects Firebase ID token in Authorization header.
    Creates the employee user record in the local database.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing Authorization header")

    id_token = auth_header.split("Bearer ", 1)[1]
    try:
        decoded = verify_firebase_token(id_token)
    except ValueError as e:
        raise UnauthorizedError(str(e))

    firebase_uid = decoded["uid"]
    email = decoded.get("email", "")

    try:
        user = user_service.register_employee(firebase_uid=firebase_uid, email=email)
    except ValidationError:
        # Already registered — return existing user
        user = user_service.get_user_by_firebase_uid(firebase_uid)

    return jsonify(user.to_dict()), 201


@auth_bp.route("/me", methods=["GET"])
def get_profile():
    """GET /api/auth/me — return the current user's profile.

    Accepts either an admin session token or a Firebase ID token.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing Authorization header")

    token = auth_header.split("Bearer ", 1)[1]

    # Check if it's an admin session token
    if is_admin_token(token):
        user = user_service.get_admin_user()
        if user:
            return jsonify(user.to_dict()), 200
        raise UnauthorizedError("Admin user not found")

    # Otherwise, verify as Firebase token
    try:
        decoded = verify_firebase_token(token)
    except ValueError as e:
        raise UnauthorizedError(str(e))

    firebase_uid = decoded["uid"]
    user = user_service.get_user_by_firebase_uid(firebase_uid)
    return jsonify(user.to_dict()), 200
