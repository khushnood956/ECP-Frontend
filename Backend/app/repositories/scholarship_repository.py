from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scholarship import Scholarship
from app.repositories.base import BaseRepository
from app.repositories.params import (
    FilterCondition,
    FilterOperator,
    PaginatedResult,
    PaginationParams,
)


class ScholarshipRepository(BaseRepository[Scholarship]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Scholarship, session=session)

    async def get_active(
        self, pagination: PaginationParams
    ) -> PaginatedResult[Scholarship]:
        filters = [
            FilterCondition(field="is_active", operator=FilterOperator.EQ, value=True)
        ]
        return await self.list_paginated(pagination=pagination, filters=filters)

    async def search(self, **kwargs: Any) -> Sequence[Scholarship]:
        """Domain specific search query."""
        return await self.list(**kwargs)

    async def list_scoped(
        self,
        pagination: PaginationParams,
        user_role: str,
        own_agency_id: str | None = None
    ) -> PaginatedResult[Scholarship]:
        import math

        from sqlalchemy import and_, func, or_, select
        
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)
        
        from app.models.enums import UserRole
        if user_role == UserRole.ADMIN:
            pass
        elif user_role == UserRole.AGENCY:
            if own_agency_id:
                cond = or_(
                    self.model.agency_id == own_agency_id,
                    and_(self.model.is_active == True, self.model.agency_id == None)
                )
            else:
                cond = and_(self.model.is_active == True, self.model.agency_id == None)
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)
        else:
            cond = self.model.is_active == True
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)
            
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

    async def list_active_scoped(
        self,
        user_role: str,
        own_agency_id: str | None = None
    ) -> Sequence[Scholarship]:
        from sqlalchemy import or_, select

        from app.models.enums import UserRole
        
        stmt = select(self.model).where(self.model.is_active == True)
        if user_role == UserRole.ADMIN:
            pass
        elif user_role == UserRole.AGENCY:
            if own_agency_id:
                cond = or_(
                    self.model.agency_id == own_agency_id,
                    self.model.agency_id == None
                )
                stmt = stmt.where(cond)
            else:
                stmt = stmt.where(self.model.agency_id == None)
        else:
            pass
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_scoped(
        self,
        user_role: str,
        own_agency_id: str | None = None,
        **kwargs: Any
    ) -> Sequence[Scholarship]:
        from sqlalchemy import and_, or_, select

        from app.models.enums import UserRole
        
        stmt = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                stmt = stmt.where(getattr(self.model, key) == value)
                
        if user_role == UserRole.ADMIN:
            pass
        elif user_role == UserRole.AGENCY:
            if own_agency_id:
                cond = or_(
                    self.model.agency_id == own_agency_id,
                    and_(self.model.is_active == True, self.model.agency_id == None)
                )
            else:
                cond = and_(self.model.is_active == True, self.model.agency_id == None)
            stmt = stmt.where(cond)
        else:
            stmt = stmt.where(self.model.is_active == True)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

