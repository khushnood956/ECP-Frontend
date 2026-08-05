from collections.abc import Sequence
from typing import Any, Protocol, TypeVar
from uuid import UUID

from app.repositories.params import (
    FilterCondition,
    PaginatedResult,
    PaginationParams,
    SortParams,
)

ModelType = TypeVar("ModelType")


class IRepository(Protocol[ModelType]):
    async def create(self, obj_in: ModelType) -> ModelType: ...

    async def get_by_id(self, id: UUID) -> ModelType | None: ...

    async def update(self, id: UUID, obj_in: dict[str, Any]) -> ModelType | None: ...

    async def delete(self, id: UUID) -> bool: ...

    async def list(self, **kwargs) -> Sequence[ModelType]: ...

    async def list_paginated(
        self,
        pagination: PaginationParams,
        sort: SortParams | None = None,
        filters: list[FilterCondition] | None = None,
    ) -> PaginatedResult[ModelType]: ...

    async def bulk_create(self, objs_in: list[ModelType]) -> list[ModelType]: ...

    async def bulk_update(self, updates: list[tuple[UUID, dict[str, Any]]]) -> int: ...

    async def bulk_delete(self, ids: list[UUID]) -> int: ...
