from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import AttendanceStatus


class AttendanceBase(BaseModel):
    class_id: UUID
    student_id: UUID
    date: date
    status: AttendanceStatus
    remarks: str | None = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: AttendanceStatus | None = None
    remarks: str | None = None


class AttendanceResponse(AttendanceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
