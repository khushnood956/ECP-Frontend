from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import DegreeLevel, Gender


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    gender: Gender | None = None
    date_of_birth: date | None = None
    country: str | None = None
    city: str | None = None
    phone: str | None = None
    highest_qualification: str | None = None
    cgpa_or_percentage: float | None = None
    preferred_degree: DegreeLevel | None = None
    preferred_country: str | None = None
    budget: float | None = None
    bio: str | None = None
    profile_picture_url: str | None = None


class StudentCreate(StudentBase):
    user_id: UUID


class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    gender: Gender | None = None
    date_of_birth: date | None = None
    country: str | None = None
    city: str | None = None
    phone: str | None = None
    highest_qualification: str | None = None
    cgpa_or_percentage: float | None = None
    preferred_degree: DegreeLevel | None = None
    preferred_country: str | None = None
    budget: float | None = None
    bio: str | None = None
    profile_picture_url: str | None = None


class StudentResponse(StudentBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
