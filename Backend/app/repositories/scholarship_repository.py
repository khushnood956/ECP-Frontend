from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.scholarship import Scholarship
from app.repositories.params import PaginationParams, PaginatedResult, FilterCondition, FilterOperator

class ScholarshipRepository(BaseRepository[Scholarship]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Scholarship, session=session)

    async def get_active(self, pagination: PaginationParams) -> PaginatedResult[Scholarship]:
        filters = [
            FilterCondition(field="is_active", operator=FilterOperator.EQ, value=True)
        ]
        return await self.list_paginated(pagination=pagination, filters=filters)
