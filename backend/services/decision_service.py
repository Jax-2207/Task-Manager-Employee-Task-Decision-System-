"""Decision service — business rules and domain logic.

State transition rules are enforced ONLY here.
Valid transitions: PROPOSED → ACCEPTED, PROPOSED → REJECTED.
No transitions allowed from ACCEPTED or REJECTED.
"""

from exceptions import InvalidStateTransitionError, NotFoundError
from models.decision import DecisionStatus
from repositories import decision_repository, user_repository
from services import user_service


# --- Allowed transitions (the single source of truth) ---
_ALLOWED_TRANSITIONS = {
    DecisionStatus.PROPOSED: {DecisionStatus.ACCEPTED, DecisionStatus.REJECTED},
}


def _validate_transition(current_status, new_status):
    """Raise InvalidStateTransitionError if the transition is not allowed."""
    allowed = _ALLOWED_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise InvalidStateTransitionError(current_status.value, new_status.value)


def get_all_decisions():
    """Return all decisions."""
    return decision_repository.get_all()


def get_decision(decision_id):
    """Return a single decision or raise NotFoundError."""
    decision = decision_repository.get_by_id(decision_id)
    if decision is None:
        raise NotFoundError("Decision", decision_id)
    return decision


def get_employee_decisions(user_id):
    """Return all decisions created by this user."""
    return decision_repository.get_by_creator(user_id)


def get_assigned_decisions(user_id):
    """Return all decisions assigned to this user."""
    return decision_repository.get_assigned_to_user(user_id)


def create_decision(title, description=None, created_by_user_id=None):
    """Create a new decision (always starts as PROPOSED)."""
    return decision_repository.create(
        title=title,
        description=description,
        created_by_user_id=created_by_user_id,
    )


def update_decision_status(decision_id, new_status_str):
    """Validate the transition and update the decision's status.

    Args:
        decision_id: Primary key of the decision.
        new_status_str: Target status as a string (e.g. "ACCEPTED").

    Raises:
        NotFoundError: If the decision doesn't exist.
        InvalidStateTransitionError: If the transition is not allowed.
    """
    decision = get_decision(decision_id)
    new_status = DecisionStatus(new_status_str)
    _validate_transition(decision.status, new_status)
    return decision_repository.update_status(decision, new_status)


def assign_decision(decision_id, employee_id_str):
    """Assign a decision to a specific employee by their employee_id string.

    Args:
        decision_id: PK of the decision.
        employee_id_str: e.g. "EMP-001"

    Raises:
        NotFoundError: If decision or employee doesn't exist.
    """
    decision = get_decision(decision_id)
    employee = user_service.get_user_by_employee_id(employee_id_str)
    return decision_repository.assign_to_user(decision, employee.id)


def assign_decision_to_all(decision_id):
    """Create a copy of the decision assigned to every employee.

    The original decision stays as-is. A new PROPOSED decision is created
    for each employee with the same title and description.

    Returns:
        List of newly created decision dicts.
    """
    original = get_decision(decision_id)
    employees = user_repository.get_all_employees()
    assigned = []
    for emp in employees:
        new_decision = decision_repository.create(
            title=original.title,
            description=original.description,
            created_by_user_id=original.created_by_user_id,
        )
        decision_repository.assign_to_user(new_decision, emp.id)
        assigned.append(new_decision)
    return assigned


def delete_decision(decision_id):
    """Delete a decision by id."""
    decision = get_decision(decision_id)
    decision_repository.delete(decision)
