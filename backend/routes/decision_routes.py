"""Decision routes — HTTP concerns only, no business logic."""

import logging

from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError

from middleware import require_auth, require_admin
from schemas.decision_schema import DecisionCreateSchema, DecisionUpdateStatusSchema
from schemas.user_schema import AssignDecisionSchema
from services import decision_service

logger = logging.getLogger(__name__)

decisions_bp = Blueprint("decisions", __name__, url_prefix="/api/decisions")

_create_schema = DecisionCreateSchema()
_update_status_schema = DecisionUpdateStatusSchema()
_assign_schema = AssignDecisionSchema()


@decisions_bp.route("", methods=["GET"])
@require_auth
def list_decisions():
    """GET /api/decisions — return decisions based on user role.

    Admin: all decisions.
    Employee: only their own decisions.
    """
    if g.user.role.value == "ADMIN":
        decisions = decision_service.get_all_decisions()
    else:
        decisions = decision_service.get_employee_decisions(g.user.id)
    return jsonify([d.to_dict() for d in decisions]), 200


@decisions_bp.route("/assigned", methods=["GET"])
@require_auth
def list_assigned_decisions():
    """GET /api/decisions/assigned — return decisions assigned to the current user."""
    decisions = decision_service.get_assigned_decisions(g.user.id)
    return jsonify([d.to_dict() for d in decisions]), 200


@decisions_bp.route("/<int:decision_id>", methods=["GET"])
@require_auth
def get_decision(decision_id):
    """GET /api/decisions/<id> — return a single decision."""
    decision = decision_service.get_decision(decision_id)
    return jsonify(decision.to_dict()), 200


@decisions_bp.route("", methods=["POST"])
@require_auth
def create_decision():
    """POST /api/decisions — create a new decision (employee proposes)."""
    json_data = request.get_json(silent=True) or {}
    data = _create_schema.load(json_data)
    decision = decision_service.create_decision(
        title=data["title"],
        description=data.get("description"),
        created_by_user_id=g.user.id,
    )
    return jsonify(decision.to_dict()), 201


@decisions_bp.route("/<int:decision_id>/status", methods=["PATCH"])
@require_admin
def update_decision_status(decision_id):
    """PATCH /api/decisions/<id>/status — admin accepts/rejects a decision."""
    json_data = request.get_json(silent=True) or {}
    data = _update_status_schema.load(json_data)
    decision = decision_service.update_decision_status(decision_id, data["status"])
    return jsonify(decision.to_dict()), 200


@decisions_bp.route("/<int:decision_id>/assign", methods=["POST"])
@require_admin
def assign_decision(decision_id):
    """POST /api/decisions/<id>/assign — admin assigns decision to an employee."""
    json_data = request.get_json(silent=True) or {}
    data = _assign_schema.load(json_data)
    decision = decision_service.assign_decision(decision_id, data["employee_id"])
    return jsonify(decision.to_dict()), 200


@decisions_bp.route("/<int:decision_id>/assign-all", methods=["POST"])
@require_admin
def assign_decision_to_all(decision_id):
    """POST /api/decisions/<id>/assign-all — admin assigns decision to all employees."""
    assigned = decision_service.assign_decision_to_all(decision_id)
    return jsonify([d.to_dict() for d in assigned]), 201


@decisions_bp.route("/<int:decision_id>", methods=["DELETE"])
@require_auth
def delete_decision(decision_id):
    """DELETE /api/decisions/<id> — delete a decision."""
    decision_service.delete_decision(decision_id)
    return jsonify({"message": "Decision deleted"}), 200
