"""Marshmallow schemas for User input validation."""

from marshmallow import Schema, fields, validate


class UserRegisterSchema(Schema):
    """Validates input for registering a new user."""

    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters."),
    )


class AssignDecisionSchema(Schema):
    """Validates input for assigning a decision to an employee."""

    employee_id = fields.String(
        required=True,
        validate=validate.Length(min=1, error="Employee ID is required."),
    )
