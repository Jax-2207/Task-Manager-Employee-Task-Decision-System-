"""Marshmallow schemas for Decision input validation and serialization."""

from marshmallow import Schema, fields, validate, validates, ValidationError


class DecisionCreateSchema(Schema):
    """Validates input for creating a new Decision."""

    title = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=200, error="Title must be 1–200 characters."),
        ],
    )
    description = fields.String(
        load_default=None,
        validate=validate.Length(max=1000, error="Description must be at most 1000 characters."),
    )

    @validates("title")
    def validate_title_not_blank(self, value):
        if not value or not value.strip():
            raise ValidationError("Title must not be blank.")


class DecisionUpdateStatusSchema(Schema):
    """Validates input for updating a Decision's status."""

    status = fields.String(
        required=True,
        validate=validate.OneOf(
            ["ACCEPTED", "REJECTED"],
            error="Status must be one of: ACCEPTED, REJECTED.",
        ),
    )
