from uuid import UUID
from pydantic import BaseModel

class ApplicationRequirementBase(BaseModel):
    field_key: str
    label: str
    field_type: str
    is_required: bool = True
    options: str | None = None
    display_order: int = 0

class ApplicationRequirementCreate(ApplicationRequirementBase):
    pass

class ApplicationRequirementResponse(ApplicationRequirementBase):
    id: str
    scholarship_id: str

    model_config = {"from_attributes": True}

class ApplicationResponseBase(BaseModel):
    requirement_id: str
    value: str | None = None
    file_url: str | None = None

class ApplicationResponseCreate(ApplicationResponseBase):
    pass

class ApplicationResponseOut(ApplicationResponseBase):
    id: str
    lead_id: str

    model_config = {"from_attributes": True}
