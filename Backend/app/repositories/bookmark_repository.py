from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bookmark import Bookmark
from app.models.scholarship import Scholarship
from app.repositories.base import BaseRepository


class BookmarkRepository(BaseRepository[Bookmark]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Bookmark, session=session)

    def _query_options(self):
        return (
            selectinload(self.model.scholarship).selectinload(Scholarship.application_requirements),
            selectinload(self.model.university),
        )

    async def get_by_id(self, id: UUID) -> Bookmark | None:
        stmt = select(self.model).where(self.model.id == str(id)).options(*self._query_options())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_student_profile_id(self, student_profile_id: UUID | str) -> list[Bookmark]:
        stmt = (
            select(self.model)
            .where(self.model.student_profile_id == str(student_profile_id))
            .options(*self._query_options())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_student_and_resource(
        self,
        student_profile_id: UUID | str,
        bookmark_type: str,
        resource_id: UUID | str,
    ) -> Bookmark | None:
        stmt = select(self.model).where(
            self.model.student_profile_id == str(student_profile_id),
            self.model.bookmark_type == bookmark_type,
        )
        if bookmark_type == "scholarship":
            stmt = stmt.where(self.model.scholarship_id == str(resource_id))
        else:
            stmt = stmt.where(self.model.university_id == str(resource_id))

        result = await self.session.execute(stmt)
        return result.scalars().first()
