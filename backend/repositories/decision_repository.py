"""Decision repository — database interaction only, no business logic."""

from datetime import datetime, timezone

from models import db
from models.decision import Decision, DecisionStatus


def get_all():
    """Return all Decision records ordered by creation date (newest first)."""
    return Decision.query.order_by(Decision.created_at.desc()).all()


def get_by_id(decision_id):
    """Return a single Decision by primary key, or None if not found."""
    return db.session.get(Decision, decision_id)


def get_by_creator(user_id):
    """Return all decisions created by a specific user."""
    return (
        Decision.query.filter_by(created_by_user_id=user_id)
        .order_by(Decision.created_at.desc())
        .all()
    )


def get_assigned_to_user(user_id):
    """Return all decisions assigned to a specific user."""
    return (
        Decision.query.filter_by(assigned_to_user_id=user_id)
        .order_by(Decision.created_at.desc())
        .all()
    )


def create(title, description=None, created_by_user_id=None):
    """Insert a new Decision with status PROPOSED."""
    decision = Decision(
        title=title,
        description=description,
        status=DecisionStatus.PROPOSED,
        created_by_user_id=created_by_user_id,
    )
    db.session.add(decision)
    db.session.commit()
    return decision


def update_status(decision, new_status):
    """Persist a status change on the given Decision object.

    The caller (service layer) is responsible for validating the transition.
    """
    decision.status = new_status
    decision.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return decision


def assign_to_user(decision, user_id):
    """Assign a decision to a user."""
    decision.assigned_to_user_id = user_id
    decision.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return decision


def delete(decision):
    """Remove a Decision from the database."""
    db.session.delete(decision)
    db.session.commit()
