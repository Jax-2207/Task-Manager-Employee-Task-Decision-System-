"""Domain-specific exceptions.

These exceptions represent business-rule violations and are mapped
to HTTP status codes by the global error handlers in app.py.
"""


class ValidationError(Exception):
    """Raised when input data fails validation."""

    def __init__(self, message="Invalid input data"):
        self.message = message
        super().__init__(self.message)


class InvalidStateTransitionError(Exception):
    """Raised when a Decision status transition violates domain rules."""

    def __init__(self, current_status, new_status):
        self.message = (
            f"Cannot transition from {current_status} to {new_status}"
        )
        super().__init__(self.message)


class NotFoundError(Exception):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity="Resource", entity_id=None):
        identifier = f" with id {entity_id}" if entity_id else ""
        self.message = f"{entity}{identifier} not found"
        super().__init__(self.message)


class UnauthorizedError(Exception):
    """Raised when authentication fails or is missing."""

    def __init__(self, message="Authentication required"):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(Exception):
    """Raised when a user lacks permission for the requested action."""

    def __init__(self, message="You do not have permission to perform this action"):
        self.message = message
        super().__init__(self.message)
