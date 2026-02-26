"""Unit tests for the Decision service layer.

Tests cover:
- Creating a decision starts as PROPOSED
- Valid transitions: PROPOSED → ACCEPTED, PROPOSED → REJECTED
- Invalid transitions (6 negative cases)
- NotFoundError for missing decisions
- Employee-scoped decisions
- Decision assignment to individual employee
- Decision assignment to all employees
"""

import pytest

from exceptions import InvalidStateTransitionError, NotFoundError
from services import decision_service


class TestCreateDecision:
    """Tests for decision creation."""

    def test_create_decision_has_proposed_status(self, app):
        """New decisions must start with PROPOSED status."""
        with app.app_context():
            decision = decision_service.create_decision(
                title="Use PostgreSQL", description="Better for production"
            )
            assert decision.status.value == "PROPOSED"
            assert decision.title == "Use PostgreSQL"
            assert decision.description == "Better for production"

    def test_create_decision_without_description(self, app):
        """Decisions can be created without a description."""
        with app.app_context():
            decision = decision_service.create_decision(title="Minimal decision")
            assert decision.status.value == "PROPOSED"
            assert decision.description is None

    def test_create_decision_with_creator(self, app, employee_user):
        """Decision records the employee who created it."""
        with app.app_context():
            decision = decision_service.create_decision(
                title="My proposal",
                description="Details here",
                created_by_user_id=employee_user["id"],
            )
            assert decision.created_by_user_id == employee_user["id"]
            assert decision.creator.employee_id == employee_user["employee_id"]


class TestValidTransitions:
    """Tests for allowed state transitions."""

    def test_proposed_to_accepted(self, app):
        """PROPOSED → ACCEPTED is a valid transition."""
        with app.app_context():
            decision = decision_service.create_decision(title="Accept me")
            updated = decision_service.update_decision_status(decision.id, "ACCEPTED")
            assert updated.status.value == "ACCEPTED"

    def test_proposed_to_rejected(self, app):
        """PROPOSED → REJECTED is a valid transition."""
        with app.app_context():
            decision = decision_service.create_decision(title="Reject me")
            updated = decision_service.update_decision_status(decision.id, "REJECTED")
            assert updated.status.value == "REJECTED"


class TestInvalidTransitions:
    """Negative tests: transitions that MUST be rejected."""

    def test_accepted_to_rejected(self, app):
        """ACCEPTED → REJECTED must raise InvalidStateTransitionError."""
        with app.app_context():
            decision = decision_service.create_decision(title="Test")
            decision_service.update_decision_status(decision.id, "ACCEPTED")
            with pytest.raises(InvalidStateTransitionError):
                decision_service.update_decision_status(decision.id, "REJECTED")

    def test_rejected_to_accepted(self, app):
        """REJECTED → ACCEPTED must raise InvalidStateTransitionError."""
        with app.app_context():
            decision = decision_service.create_decision(title="Test")
            decision_service.update_decision_status(decision.id, "REJECTED")
            with pytest.raises(InvalidStateTransitionError):
                decision_service.update_decision_status(decision.id, "ACCEPTED")

    def test_accepted_to_proposed(self, app):
        """ACCEPTED → PROPOSED must raise InvalidStateTransitionError."""
        with app.app_context():
            decision = decision_service.create_decision(title="Test")
            decision_service.update_decision_status(decision.id, "ACCEPTED")
            with pytest.raises(InvalidStateTransitionError):
                decision_service.update_decision_status(decision.id, "PROPOSED")

    def test_rejected_to_proposed(self, app):
        """REJECTED → PROPOSED must raise InvalidStateTransitionError."""
        with app.app_context():
            decision = decision_service.create_decision(title="Test")
            decision_service.update_decision_status(decision.id, "REJECTED")
            with pytest.raises(InvalidStateTransitionError):
                decision_service.update_decision_status(decision.id, "PROPOSED")

    def test_accepted_to_accepted(self, app):
        """ACCEPTED → ACCEPTED (re-transition) must raise InvalidStateTransitionError."""
        with app.app_context():
            decision = decision_service.create_decision(title="Test")
            decision_service.update_decision_status(decision.id, "ACCEPTED")
            with pytest.raises(InvalidStateTransitionError):
                decision_service.update_decision_status(decision.id, "ACCEPTED")

    def test_rejected_to_rejected(self, app):
        """REJECTED → REJECTED (re-transition) must raise InvalidStateTransitionError."""
        with app.app_context():
            decision = decision_service.create_decision(title="Test")
            decision_service.update_decision_status(decision.id, "REJECTED")
            with pytest.raises(InvalidStateTransitionError):
                decision_service.update_decision_status(decision.id, "REJECTED")


class TestNotFound:
    """Tests for missing entity handling."""

    def test_get_nonexistent_decision(self, app):
        """Requesting a decision that doesn't exist must raise NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                decision_service.get_decision(9999)

    def test_update_nonexistent_decision(self, app):
        """Updating a decision that doesn't exist must raise NotFoundError."""
        with app.app_context():
            with pytest.raises(NotFoundError):
                decision_service.update_decision_status(9999, "ACCEPTED")


class TestEmployeeScoping:
    """Tests for employee-scoped decision queries."""

    def test_get_employee_decisions(self, app, employee_user):
        """Employee sees only their own decisions."""
        with app.app_context():
            decision_service.create_decision(
                title="My decision", created_by_user_id=employee_user["id"]
            )
            decision_service.create_decision(title="Other decision")

            my_decisions = decision_service.get_employee_decisions(employee_user["id"])
            assert len(my_decisions) == 1
            assert my_decisions[0].title == "My decision"


class TestDecisionAssignment:
    """Tests for assigning decisions to employees."""

    def test_assign_to_employee(self, app, employee_user):
        """Admin assigns decision to a specific employee by employee_id."""
        with app.app_context():
            decision = decision_service.create_decision(title="Assigned task")
            updated = decision_service.assign_decision(
                decision.id, employee_user["employee_id"]
            )
            assert updated.assigned_to_user_id == employee_user["id"]

    def test_get_assigned_decisions(self, app, employee_user):
        """Employee sees decisions assigned to them."""
        with app.app_context():
            decision = decision_service.create_decision(title="Assigned task")
            decision_service.assign_decision(decision.id, employee_user["employee_id"])

            assigned = decision_service.get_assigned_decisions(employee_user["id"])
            assert len(assigned) == 1
            assert assigned[0].title == "Assigned task"

    def test_assign_to_all(self, app, employee_user, employee_user_2):
        """Admin assigns to all employees — creates copies."""
        with app.app_context():
            original = decision_service.create_decision(title="For everyone")
            assigned = decision_service.assign_decision_to_all(original.id)
            assert len(assigned) == 2

            # Each employee should have one assigned
            emp1_assigned = decision_service.get_assigned_decisions(employee_user["id"])
            emp2_assigned = decision_service.get_assigned_decisions(employee_user_2["id"])
            assert len(emp1_assigned) == 1
            assert len(emp2_assigned) == 1

    def test_assign_to_nonexistent_employee(self, app):
        """Assigning to non-existent employee must raise NotFoundError."""
        with app.app_context():
            decision = decision_service.create_decision(title="Test")
            with pytest.raises(NotFoundError):
                decision_service.assign_decision(decision.id, "EMP-999")
