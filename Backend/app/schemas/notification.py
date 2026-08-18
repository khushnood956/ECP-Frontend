from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str
    related_entity_id: UUID | None = None


class NotificationCreate(NotificationBase):
    user_id: UUID


class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
