from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import DegreeLevel, FundingType


class ScholarshipBase(BaseModel):
    title: str
    country: str
    university: str | None = None
    degree_level: DegreeLevel
    funding_type: FundingType
    amount: float | None = None
    currency: str | None = None
    deadline: date | None = None
    eligibility: str | None = None
    description: str | None = None
    application_link: str | None = None
    is_active: bool = True


class ScholarshipCreate(ScholarshipBase):
    agency_id: str | None = None


class ScholarshipUpdate(BaseModel):
    title: str | None = None
    country: str | None = None
    university: str | None = None
    degree_level: DegreeLevel | None = None
    funding_type: FundingType | None = None
    amount: float | None = None
    currency: str | None = None
    deadline: date | None = None
    eligibility: str | None = None
    description: str | None = None
    application_link: str | None = None


class ScholarshipResponse(ScholarshipBase):
    id: UUID
    agency_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
