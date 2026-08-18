from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator

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
    application_requirements: list[dict] | None = None


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
    application_requirements: list[dict] | None = None


class ScholarshipResponse(ScholarshipBase):
    id: UUID
    agency_id: str | None = None
    created_at: datetime
    updated_at: datetime
    application_requirements: list[dict] | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_application_requirements(cls, data: Any) -> Any:
        if not hasattr(data, "id"):
            return data

        def safe_get(attr_name: str) -> Any:
            return getattr(data, attr_name, None)

        application_requirements = None
        if hasattr(data, "application_requirements") and data.application_requirements is not None:
            application_requirements = []
            for requirement in data.application_requirements:
                application_requirements.append(
                    {
                        "id": getattr(requirement, "id", None),
                        "scholarship_id": getattr(requirement, "scholarship_id", None),
                        "field_key": getattr(requirement, "field_key", None),
                        "label": getattr(requirement, "label", None),
                        "field_type": getattr(requirement, "field_type", None),
                        "is_required": getattr(requirement, "is_required", None),
                        "options": getattr(requirement, "options", None),
                        "display_order": getattr(requirement, "display_order", None),
                    }
                )

        return {
            "id": safe_get("id"),
            "title": safe_get("title"),
            "country": safe_get("country"),
            "university": safe_get("university"),
            "degree_level": safe_get("degree_level"),
            "funding_type": safe_get("funding_type"),
            "amount": safe_get("amount"),
            "currency": safe_get("currency"),
            "deadline": safe_get("deadline"),
            "eligibility": safe_get("eligibility"),
            "description": safe_get("description"),
            "application_link": safe_get("application_link"),
            "is_active": safe_get("is_active"),
            "agency_id": safe_get("agency_id"),
            "created_at": safe_get("created_at"),
            "updated_at": safe_get("updated_at"),
            "application_requirements": application_requirements,
        }

    model_config = {"from_attributes": True}
