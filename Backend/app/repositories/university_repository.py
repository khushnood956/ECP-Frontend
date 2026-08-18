from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.university import University
from app.repositories.base import BaseRepository
from app.repositories.params import PaginatedResult, PaginationParams


class UniversityRepository(BaseRepository[University]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=University, session=session)

    async def list_universities(
        self, pagination: PaginationParams
    ) -> PaginatedResult[University]:
        return await self.list_paginated(pagination=pagination)

    async def search(self, **kwargs: Any) -> Sequence[University]:
        stmt = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                if key in ["name", "location"] and isinstance(value, str):
                    stmt = stmt.where(getattr(self.model, key).ilike(f"%{value}%"))
                else:
                    stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
