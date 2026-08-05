from fastapi import status

from app.core.exceptions.base import ApplicationException


class ValidationException(ApplicationException):
    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundException(ApplicationException):
    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details,
        )


class ConflictException(ApplicationException):
    def __init__(self, message: str = "Resource conflict", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            details=details,
        )


class UnauthorizedException(ApplicationException):
    def __init__(self, message: str = "Unauthorized access", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            details=details,
        )


class ForbiddenException(ApplicationException):
    def __init__(self, message: str = "Access forbidden", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            details=details,
        )


class BusinessRuleException(ApplicationException):
    def __init__(self, message: str = "Business rule violation", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_RULE_VIOLATION",
            details=details,
        )


class ServiceUnavailableException(ApplicationException):
    def __init__(self, message: str = "Service unavailable", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
            details=details,
        )


class InternalServerException(ApplicationException):
    def __init__(self, message: str = "Internal server error", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            details=details,
        )
