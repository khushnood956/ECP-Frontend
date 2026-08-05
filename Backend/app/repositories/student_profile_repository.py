from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student_profile import StudentProfile
from app.repositories.base import BaseRepository


class StudentProfileRepository(BaseRepository[StudentProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=StudentProfile, session=session)

    async def get_by_user_id(self, user_id: UUID | str) -> StudentProfile | None:
        stmt = select(self.model).where(self.model.user_id == str(user_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
