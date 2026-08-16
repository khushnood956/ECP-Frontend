from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ClassBase(BaseModel):
    name: str
    code: str
    instructor_id: UUID


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    instructor_id: UUID | None = None


class ClassResponse(ClassBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
