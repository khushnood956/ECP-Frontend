from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UniversityBase(BaseModel):
    name: str
    location: str
    ranking: str | None = None
    type: str | None = None
    tuition_category: str | None = None
    programs: list[str] | None = None


class UniversityCreate(UniversityBase):
    pass


class UniversityUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    ranking: str | None = None
    type: str | None = None
    tuition_category: str | None = None
    programs: list[str] | None = None


class UniversityResponse(UniversityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
