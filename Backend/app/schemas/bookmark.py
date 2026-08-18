from datetime import datetime

from pydantic import BaseModel

from app.schemas.scholarship import ScholarshipResponse
from app.schemas.university import UniversityResponse


from uuid import UUID

class BookmarkBase(BaseModel):
    bookmark_type: str  # "scholarship" or "university"
    scholarship_id: UUID | None = None
    university_id: UUID | None = None


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkResponse(BookmarkBase):
    id: UUID
    student_profile_id: UUID
    created_at: datetime
    updated_at: datetime
    scholarship: ScholarshipResponse | None = None
    university: UniversityResponse | None = None

    model_config = {"from_attributes": True}
