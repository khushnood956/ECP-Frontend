import math
from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import asc
from sqlalchemy import delete as sa_delete
from sqlalchemy import desc, func, select
from sqlalchemy import update as sa_update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.exceptions import RepositoryError
from app.repositories.interfaces import IRepository
from app.repositories.params import (
    FilterCondition,
    FilterOperator,
    PaginatedResult,
    PaginationParams,
    SortParams,
)

ModelType = TypeVar("ModelType")


class BaseRepository(IRepository[ModelType], Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, obj_in: ModelType) -> ModelType:
        try:
            self.session.add(obj_in)
            await self.session.flush()
            await self.session.refresh(obj_in)
            return obj_in
        except IntegrityError as e:
            raise RepositoryError(
                "Integrity error during creation", details={"error": str(e)}
            ) from e
        except SQLAlchemyError as e:
            raise RepositoryError(
                "Database error during creation", details={"error": str(e)}
            ) from e

    async def get_by_id(self, id: UUID) -> ModelType | None:
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError(
                "Database error during get_by_id", details={"error": str(e)}
            ) from e

    async def update(self, id: UUID, obj_in: dict[str, Any]) -> ModelType | None:
        if not obj_in:
            return await self.get_by_id(id)

        try:
            stmt = sa_update(self.model).where(self.model.id == id).values(**obj_in)
            await self.session.execute(stmt)
            await self.session.flush()
            return await self.get_by_id(id)
        except IntegrityError as e:
            raise RepositoryError(
                "Integrity error during update", details={"error": str(e)}
            ) from e
        except SQLAlchemyError as e:
            raise RepositoryError(
                "Database error during update", details={"error": str(e)}
            ) from e

    async def delete(self, id: UUID) -> bool:
        try:
            stmt = sa_delete(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            await self.session.flush()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            raise RepositoryError(
                "Database error during deletion", details={"error": str(e)}
            ) from e

    async def list(self, **kwargs) -> Sequence[ModelType]:
        try:
            stmt = select(self.model)
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)

            result = await self.session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise RepositoryError(
                "Database error during list", details={"error": str(e)}
            ) from e

    async def list_paginated(
        self,
        pagination: PaginationParams,
        sort: SortParams | None = None,
        filters: list[FilterCondition] | None = None,
    ) -> PaginatedResult[ModelType]:
        try:
            stmt = select(self.model)
            count_stmt = select(func.count()).select_from(self.model)

            if filters:
                for f in filters:
                    if not hasattr(self.model, f.field):
                        raise RepositoryError(
                            f"Field {f.field} does not exist on {self.model.__name__}"
                        )

                    column = getattr(self.model, f.field)

                    if f.operator == FilterOperator.EQ:
                        condition = column == f.value
                    elif f.operator == FilterOperator.NE:
                        condition = column != f.value
                    elif f.operator == FilterOperator.GT:
                        condition = column > f.value
                    elif f.operator == FilterOperator.GTE:
                        condition = column >= f.value
                    elif f.operator == FilterOperator.LT:
                        condition = column < f.value
                    elif f.operator == FilterOperator.LTE:
                        condition = column <= f.value
                    elif f.operator == FilterOperator.IN:
                        if not isinstance(f.value, list):
                            raise RepositoryError(
                                f"Value for IN operator must be a list for field {f.field}"
                            )
                        condition = column.in_(f.value)
                    elif f.operator == FilterOperator.LIKE:
                        # ilike for case-insensitive
                        condition = column.ilike(f"%{f.value}%")
                    elif f.operator == FilterOperator.IS_NULL:
                        condition = column.is_(None) if f.value else column.is_not(None)
                    else:
                        raise RepositoryError(
                            f"Unsupported filter operator {f.operator}"
                        )

                    stmt = stmt.where(condition)
                    count_stmt = count_stmt.where(condition)

            if sort and sort.sort_by:
                if not hasattr(self.model, sort.sort_by):
                    raise RepositoryError(
                        f"Sort field {sort.sort_by} does not exist on {self.model.__name__}"
                    )

                sort_col = getattr(self.model, sort.sort_by)
                if sort.sort_order == "desc":
                    stmt = stmt.order_by(desc(sort_col))
                else:
                    stmt = stmt.order_by(asc(sort_col))

            total_result = await self.session.execute(count_stmt)
            total = total_result.scalar_one()

            offset = (pagination.page - 1) * pagination.page_size
            stmt = stmt.offset(offset).limit(pagination.page_size)

            result = await self.session.execute(stmt)
            items = list(result.scalars().all())

            total_pages = (
                math.ceil(total / pagination.page_size)
                if pagination.page_size > 0
                else 0
            )

            return PaginatedResult(
                items=items,
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=total_pages,
            )
        except RepositoryError:
            raise
        except SQLAlchemyError as e:
            raise RepositoryError(
                "Database error during pagination list", details={"error": str(e)}
            ) from e

    async def bulk_create(self, objs_in: list[ModelType]) -> list[ModelType]:
        if not objs_in:
            return []
        try:
            self.session.add_all(objs_in)
            await self.session.flush()
            return objs_in
        except IntegrityError as e:
            raise RepositoryError(
                "Integrity error during bulk creation", details={"error": str(e)}
            ) from e
        except SQLAlchemyError as e:
            raise RepositoryError(
                "Database error during bulk creation", details={"error": str(e)}
            ) from e

    async def bulk_update(self, updates: list[tuple[UUID, dict[str, Any]]]) -> int:
        if not updates:
            return 0
        try:
            total_affected = 0
            for id_val, obj_in in updates:
                if not obj_in:
                    continue
                stmt = (
                    sa_update(self.model)
                    .where(self.model.id == id_val)
                    .values(**obj_in)
                )
                res = await self.session.execute(stmt)
                total_affected += res.rowcount
            await self.session.flush()
            return total_affected
        except IntegrityError as e:
            raise RepositoryError(
                "Integrity error during bulk update", details={"error": str(e)}
            ) from e
        except SQLAlchemyError as e:
            raise RepositoryError(
                "Database error during bulk update", details={"error": str(e)}
            ) from e

    async def bulk_delete(self, ids: list[UUID]) -> int:
        if not ids:
            return 0
        try:
            stmt = sa_delete(self.model).where(self.model.id.in_(ids))
            result = await self.session.execute(stmt)
            await self.session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            raise RepositoryError(
                "Database error during bulk deletion", details={"error": str(e)}
            ) from e
