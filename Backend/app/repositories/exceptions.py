from fastapi import status

from app.core.exceptions.base import ApplicationException


class RepositoryError(ApplicationException):
    def __init__(
        self, 
        message: str = "A database error occurred", 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "REPOSITORY_ERROR",
        details: dict | None = None
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=details,
        )


class EntityNotFoundError(RepositoryError):
    def __init__(self, message: str = "Entity not found", details: dict | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ENTITY_NOT_FOUND",
            details=details,
        )
