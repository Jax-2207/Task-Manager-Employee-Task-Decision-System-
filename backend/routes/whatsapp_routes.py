"""WhatsApp / OpenClaw integration routes.

Public API endpoint that allows employees to query their assigned tasks
by sending their employee ID. No authentication required — designed to
be called from WhatsApp bots (OpenClaw, Twilio, etc.).
"""

import logging

from flask import Blueprint, jsonify, request

from repositories import user_repository, decision_repository

logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint("whatsapp", __name__, url_prefix="/api/whatsapp")


@whatsapp_bp.route("/tasks", methods=["GET", "POST"])
def get_employee_tasks():
    """GET/POST /api/whatsapp/tasks — query tasks by employee ID.

    Accepts:
      - GET: ?employee_id=EMP-001
      - POST: { "employee_id": "EMP-001" }
      - POST: { "message": "EMP-001" }  (for OpenClaw/chatbot body)

    Returns a text-formatted response suitable for WhatsApp display.
    """
    employee_id = None

    if request.method == "GET":
        employee_id = request.args.get("employee_id", "").strip()
    else:
        json_data = request.get_json(silent=True) or {}
        employee_id = (
            json_data.get("employee_id", "")
            or json_data.get("message", "")
            or json_data.get("text", "")
            or json_data.get("body", "")
        ).strip().upper()

    if not employee_id:
        return jsonify({
            "reply": "👋 Welcome to Task Manager!\n\nPlease send your Employee ID (e.g. EMP-001) to see your assigned tasks.",
        }), 200

    # Look up the employee
    user = user_repository.get_by_employee_id(employee_id)
    if not user:
        return jsonify({
            "reply": f"❌ Employee ID '{employee_id}' not found.\n\nPlease check your ID and try again.",
        }), 200

    # Get assigned tasks
    assigned = decision_repository.get_assigned_to_user(user.id)
    # Also get tasks they created
    created = decision_repository.get_by_creator(user.id)

    # Format response for WhatsApp
    lines = [f"👤 *{user.email}* ({user.employee_id})\n"]

    if assigned:
        lines.append(f"📋 *Assigned Tasks ({len(assigned)}):*")
        for i, task in enumerate(assigned, 1):
            status_emoji = {"PROPOSED": "🟡", "ACCEPTED": "🟢", "REJECTED": "🔴"}.get(task.status.value, "⚪")
            lines.append(f"  {i}. {status_emoji} {task.title} [{task.status.value}]")
            if task.description:
                lines.append(f"     _{task.description[:80]}_")
    else:
        lines.append("📋 No tasks assigned to you yet.")

    lines.append("")

    if created:
        lines.append(f"✍️ *Tasks You Created ({len(created)}):*")
        for i, task in enumerate(created, 1):
            status_emoji = {"PROPOSED": "🟡", "ACCEPTED": "🟢", "REJECTED": "🔴"}.get(task.status.value, "⚪")
            lines.append(f"  {i}. {status_emoji} {task.title} [{task.status.value}]")
    else:
        lines.append("✍️ You haven't created any tasks yet.")

    reply = "\n".join(lines)

    return jsonify({
        "reply": reply,
        "employee": user.to_dict(),
        "assigned_tasks": [t.to_dict() for t in assigned],
        "created_tasks": [t.to_dict() for t in created],
    }), 200
