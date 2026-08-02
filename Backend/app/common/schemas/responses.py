from typing import Any, Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")

class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response format."""
    success: bool = True
    message: str
    data: Optional[T] = None
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = False
    message: str
    error_code: str
    details: Optional[dict[str, Any]] = None
    request_id: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated success response format."""
    success: bool = True
    message: str
    data: List[T]
    total: int
    page: int
    size: int
    request_id: Optional[str] = None
