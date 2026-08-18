from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lead import Lead
from app.repositories.base import BaseRepository
from app.repositories.exceptions import RepositoryError
from app.repositories.params import FilterOperator, PaginatedResult


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Lead, session=session)

    def _query_options(self):
        return (
            selectinload(self.model.scholarship),
            selectinload(self.model.application_responses),
        )

    async def get_by_id(self, id: UUID) -> Lead | None:
        stmt = select(self.model).where(self.model.id == str(id)).options(*self._query_options())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_student_id(self, student_id: UUID | str) -> list[Lead]:
        stmt = select(self.model).where(self.model.student_id == str(student_id)).options(
            *self._query_options()
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_agency_id(self, agency_id: UUID | str) -> list[Lead]:
        stmt = select(self.model).where(self.model.agency_id == str(agency_id)).options(
            *self._query_options()
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_scholarship_id(self, scholarship_id: UUID | str) -> list[Lead]:
        stmt = select(self.model).where(
            self.model.scholarship_id == str(scholarship_id)
        ).options(
            *self._query_options()
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_paginated(self, pagination, sort=None, filters=None):
        import math

        from sqlalchemy import asc, desc, func, select

        stmt = select(self.model).options(*self._query_options())
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
