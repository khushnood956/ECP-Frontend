class ServiceException(Exception):
    """
    Base exception for all service layer errors.
    This serves as the parent class for specific domain exceptions,
    allowing the API layer to catch and translate them appropriately.
    """
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class BusinessRuleViolation(ServiceException):
    """Raised when an operation violates a domain business rule."""
    pass


class EntityAlreadyExists(ServiceException):
    """Raised when attempting to create an entity that conflicts with an existing one."""
    pass


class EntityNotFound(ServiceException):
    """Raised when a requested entity cannot be found in the system."""
    pass


class PermissionDenied(ServiceException):
    """Raised when the current user does not have permission to perform the requested action."""
    pass


class ValidationFailure(ServiceException):
    """Raised when data validation fails at the service or domain level."""
    pass
