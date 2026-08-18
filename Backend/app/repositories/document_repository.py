from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Document, session=session)

    async def get_by_student_profile_id(self, student_profile_id: UUID | str) -> list[Document]:
        stmt = select(self.model).where(self.model.student_profile_id == str(student_profile_id))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
