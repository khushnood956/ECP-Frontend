from typing import Any
from uuid import UUID

from app.models.notification import Notification
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService
from app.services.exceptions import EntityNotFound, PermissionDenied


class NotificationService(BaseService[Notification, Any, Any]):
    repository: NotificationRepository

    def __init__(
        self,
        repository: NotificationRepository,
        transaction_manager: TransactionManager,
    ):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    async def list_notifications(self, current_user: User) -> list[Notification]:
        return await self.repository.get_by_user_id(current_user.id)

    async def create_notification(
        self,
        user_id: UUID | str,
        title: str,
        message: str,
        related_entity_id: UUID | str | None = None,
    ) -> Notification:
        async with self.transaction_manager.transaction():
            notification = Notification(
                user_id=str(user_id),
                title=title,
                message=message,
                related_entity_id=str(related_entity_id) if related_entity_id else None,
                is_read=False,
            )
            created = await self.repository.create(notification)
            return created

    async def mark_as_read(self, notification_id: UUID | str, current_user: User) -> Notification:
        uuid_val = UUID(str(notification_id))
        notification = await self.repository.get_by_id(uuid_val)
        if not notification:
            raise EntityNotFound(f"Notification with id {notification_id} not found.")

        if notification.user_id != str(current_user.id):
            raise PermissionDenied("You do not have permission to modify this notification.")

        async with self.transaction_manager.transaction():
            updated = await self.repository.update(uuid_val, {"is_read": True})
            if not updated:
                raise EntityNotFound(f"Notification with id {notification_id} not found.")
            return updated

    async def mark_all_read(self, current_user: User) -> None:
        async with self.transaction_manager.transaction():
            await self.repository.mark_all_read(current_user.id)

    async def delete_notification(self, notification_id: UUID | str, current_user: User) -> bool:
        uuid_val = UUID(str(notification_id))
        notification = await self.repository.get_by_id(uuid_val)
        if not notification:
            raise EntityNotFound(f"Notification with id {notification_id} not found.")

        if notification.user_id != str(current_user.id):
            raise PermissionDenied("You do not have permission to delete this notification.")

        async with self.transaction_manager.transaction():
            await self.repository.delete(uuid_val)
            return True
