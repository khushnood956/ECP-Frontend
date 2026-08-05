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
    pass


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
    is_active: bool | None = None


class ScholarshipResponse(ScholarshipBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
