from enum import Enum
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

ModelType = TypeVar("ModelType")


class FilterOperator(str, Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    LIKE = "like"
    IS_NULL = "is_null"


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SortParams(BaseModel):
    sort_by: str | None = None
    sort_order: Literal["asc", "desc"] = "asc"


class FilterCondition(BaseModel):
    field: str
    operator: FilterOperator
    value: Any


class PaginatedResult(BaseModel, Generic[ModelType]):
    items: list[ModelType]
    total: int
    page: int
    page_size: int
    total_pages: int
