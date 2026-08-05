from fastapi import status

from app.core.exceptions.base import ApplicationException


class RepositoryError(ApplicationException):
    def __init__(
        self, message: str = "A database error occurred", details: dict = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="REPOSITORY_ERROR",
            details=details,
        )


class EntityNotFoundError(RepositoryError):
    def __init__(self, message: str = "Entity not found", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ENTITY_NOT_FOUND",
            details=details,
        )
