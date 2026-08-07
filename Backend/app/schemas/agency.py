from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import AgencyVerificationStatus


class AgencyBase(BaseModel):
    agency_name: str
    description: str | None = None
    website: str | None = None
    logo_url: str | None = None
    registration_number: str | None = None
    email: str | None = None
    phone: str | None = None
    country: str | None = None
    city: str | None = None
    address: str | None = None


class AgencyCreate(AgencyBase):
    pass



class AgencyUpdate(BaseModel):
    agency_name: str | None = None
    description: str | None = None
    website: str | None = None
    logo_url: str | None = None
    registration_number: str | None = None
    email: str | None = None
    phone: str | None = None
    country: str | None = None
    city: str | None = None
    address: str | None = None


class AgencyResponse(AgencyBase):
    id: UUID
    user_id: UUID
    verification_status: AgencyVerificationStatus
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
