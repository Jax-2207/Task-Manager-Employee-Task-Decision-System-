"""Decision model — pure data container, no business logic."""

import enum
from datetime import datetime, timezone

from models import db


class DecisionStatus(enum.Enum):
    """Valid statuses for a Decision."""

    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Decision(db.Model):
    """Represents an architectural or engineering decision."""

    __tablename__ = "decisions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum(DecisionStatus),
        nullable=False,
        default=DecisionStatus.PROPOSED,
    )
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    assigned_to_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Serialize to a plain dictionary."""
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_by_user_id": self.created_by_user_id,
            "created_by_employee_id": self.creator.employee_id if self.creator else None,
            "created_by_email": self.creator.email if self.creator else None,
            "assigned_to_user_id": self.assigned_to_user_id,
            "assigned_to_employee_id": self.assignee.employee_id if self.assignee else None,
            "assigned_to_email": self.assignee.email if self.assignee else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return result
