from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator

import json


def parse_notes_field(notes_str: str | None) -> tuple[str | None, str | None, str | None]:
    if not notes_str:
        return None, None, None
    try:
        data = json.loads(notes_str)
        if isinstance(data, dict):
            return data.get("motivation_letter"), data.get("documents"), data.get("notes")
    except Exception:
        pass
    return None, None, notes_str


def serialize_notes_field(motivation_letter: str | None, documents: str | None, notes: str | None) -> str:
    return json.dumps({
        "motivation_letter": motivation_letter,
        "documents": documents,
        "notes": notes
    })


class LeadCreate(BaseModel):
    scholarship_id: UUID
    motivation_letter: str | None = None
    notes: str | None = None
    documents: str | None = None


class LeadUpdate(BaseModel):
    motivation_letter: str | None = None
    notes: str | None = None
    documents: str | None = None


class LeadStatusUpdate(BaseModel):
    status: str


class LeadPatchRequest(BaseModel):
    motivation_letter: str | None = None
    documents: str | None = None
    notes: str | None = None
    status: str | None = None



class LeadResponse(BaseModel):
    id: UUID
    student_id: UUID
    scholarship_id: UUID
    agency_id: UUID | None = None
    status: str
    motivation_letter: str | None = None
    documents: str | None = None
    notes: str | None = None
    status_updated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def custom_validate(cls, data: Any) -> Any:
        if not hasattr(data, "id"):
            return data
        
        status_map = {
            "NEW": "submitted",
            "CONTACTED": "under_review",
            "IN_PROGRESS": "under_review",
            "WON": "accepted",
            "LOST": "rejected"
        }
        status_str = status_map.get(data.status.name if hasattr(data.status, "name") else str(data.status), "submitted")

        mot_let, docs, notes_val = parse_notes_field(data.notes)

        return {
            "id": data.id,
            "student_id": UUID(data.student_id) if isinstance(data.student_id, str) else data.student_id,
            "scholarship_id": UUID(data.scholarship_id) if isinstance(data.scholarship_id, str) else data.scholarship_id,
            "agency_id": (UUID(data.agency_id) if isinstance(data.agency_id, str) else data.agency_id) if data.agency_id else None,
            "status": status_str,
            "motivation_letter": mot_let,
            "documents": docs,
            "notes": notes_val,
            "status_updated_at": data.status_updated_at,
            "created_at": data.created_at,
            "updated_at": data.updated_at
        }

    class Config:
        from_attributes = True
