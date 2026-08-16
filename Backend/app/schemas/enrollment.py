from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import EnrollmentStatus


class EnrollmentBase(BaseModel):
    class_id: UUID
    student_id: UUID
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    status: EnrollmentStatus | None = None


class EnrollmentResponse(EnrollmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
