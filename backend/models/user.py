"""User model — stored in SQLAlchemy (relational DB), not Firebase."""

import enum
from datetime import datetime, timezone

from models import db


class UserRole(enum.Enum):
    """User roles in the system."""

    ADMIN = "ADMIN"
    EMPLOYEE = "EMPLOYEE"


class User(db.Model):
    """Represents a registered user with a role and an employee ID."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(
        db.Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE
    )
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    created_decisions = db.relationship(
        "Decision", foreign_keys="Decision.created_by_user_id", backref="creator", lazy=True
    )
    assigned_decisions = db.relationship(
        "Decision", foreign_keys="Decision.assigned_to_user_id", backref="assignee", lazy=True
    )

    def to_dict(self):
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "email": self.email,
            "role": self.role.value,
            "employee_id": self.employee_id,
            "created_at": self.created_at.isoformat(),
        }
