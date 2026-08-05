from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Lead, session=session)

    async def get_by_student_id(self, student_id: UUID | str) -> list[Lead]:
        stmt = select(self.model).where(self.model.student_id == str(student_id))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_agency_id(self, agency_id: UUID | str) -> list[Lead]:
        stmt = select(self.model).where(self.model.agency_id == str(agency_id))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_scholarship_id(self, scholarship_id: UUID | str) -> list[Lead]:
        stmt = select(self.model).where(
            self.model.scholarship_id == str(scholarship_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
