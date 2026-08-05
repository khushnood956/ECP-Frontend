from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.agency import Agency

class AgencyRepository(BaseRepository[Agency]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Agency, session=session)

    async def get_by_user_id(self, user_id: UUID | str) -> Optional[Agency]:
        stmt = select(self.model).where(self.model.user_id == str(user_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_registration_number(self, registration_number: str) -> Optional[Agency]:
        stmt = select(self.model).where(self.model.registration_number == registration_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
