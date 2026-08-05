from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import LeadStatus


class LeadBase(BaseModel):
    notes: str | None = None
    follow_up_date: datetime | None = None


class LeadCreate(LeadBase):
    student_id: UUID
    scholarship_id: UUID
    agency_id: UUID | None = None


class LeadUpdate(BaseModel):
    notes: str | None = None
    follow_up_date: datetime | None = None


class LeadResponse(LeadBase):
    id: UUID
    student_id: UUID
    scholarship_id: UUID
    agency_id: UUID | None = None
    status: LeadStatus
    status_updated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
