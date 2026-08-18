from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Notification, session=session)

    async def get_by_user_id(self, user_id: UUID | str) -> list[Notification]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == str(user_id))
            .order_by(self.model.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_all_read(self, user_id: UUID | str) -> None:
        stmt = select(self.model).where(
            self.model.user_id == str(user_id), self.model.is_read == False
        )
        result = await self.session.execute(stmt)
        notifications = result.scalars().all()
        for n in notifications:
            n.is_read = True
        # Base class transaction manager commits this when completed
