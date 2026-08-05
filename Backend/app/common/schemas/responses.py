from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response format."""

    success: bool = True
    message: str
    data: T | None = None
    request_id: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response format."""

    success: bool = False
    message: str
    error_code: str
    details: dict[str, Any] | None = None
    request_id: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated success response format."""

    success: bool = True
    message: str
    data: list[T]
    total: int
    page: int
    size: int
    request_id: str | None = None
