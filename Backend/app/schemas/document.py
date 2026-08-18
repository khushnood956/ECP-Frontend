from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentBase(BaseModel):
    filename: str
    doc_type: str

class DocumentResponse(DocumentBase):
    id: UUID
    student_profile_id: UUID
    verified: bool
    upload_date: date
    file_size: int
    mime_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
