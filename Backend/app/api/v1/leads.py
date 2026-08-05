from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.services import get_lead_service
from app.models.enums import LeadStatus
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.services.lead_service import LeadService

router = APIRouter()


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class LeadFollowUpUpdate(BaseModel):
    notes: str


@router.post(
    "",
    response_model=SuccessResponse[LeadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a lead",
)
async def create_lead(
    lead_in: LeadCreate, service: LeadService = Depends(get_lead_service)
):
    lead = await service.create(lead_in)
    return success_response(
        data=LeadResponse.model_validate(lead),
        message="Lead created successfully",
        status_code=201,
    )


@router.get(
    "/{id}", response_model=SuccessResponse[LeadResponse], summary="Get a lead by ID"
)
async def get_lead(id: UUID, service: LeadService = Depends(get_lead_service)):
    lead = await service.get(id)
    return success_response(
        data=LeadResponse.model_validate(lead), message="Lead retrieved successfully"
    )


@router.get(
    "", response_model=SuccessResponse[list[LeadResponse]], summary="Get all leads"
)
async def get_leads(
    skip: int = 0, limit: int = 100, service: LeadService = Depends(get_lead_service)
):
    leads, total = await service.get_all(skip=skip, limit=limit)
    data = [LeadResponse.model_validate(l) for l in leads]
    return success_response(data=data, message="Leads retrieved successfully")


@router.patch(
    "/{id}", response_model=SuccessResponse[LeadResponse], summary="Update a lead"
)
async def update_lead(
    id: UUID, lead_in: LeadUpdate, service: LeadService = Depends(get_lead_service)
):
    lead = await service.update(id, lead_in)
    return success_response(
        data=LeadResponse.model_validate(lead), message="Lead updated successfully"
    )


@router.delete("/{id}", response_model=SuccessResponse, summary="Delete a lead")
async def delete_lead(id: UUID, service: LeadService = Depends(get_lead_service)):
    await service.delete(id)
    return success_response(message="Lead deleted successfully")


@router.post(
    "/{id}/assign-agency",
    response_model=SuccessResponse[LeadResponse],
    summary="Assign an agency to a lead",
)
async def assign_agency(
    id: UUID, agency_id: UUID, service: LeadService = Depends(get_lead_service)
):
    lead = await service.assign_to_agency(id, agency_id)
    return success_response(
        data=LeadResponse.model_validate(lead), message="Agency assigned successfully"
    )


@router.post(
    "/{id}/status",
    response_model=SuccessResponse[LeadResponse],
    summary="Update lead status",
)
async def update_lead_status(
    id: UUID,
    status_update: LeadStatusUpdate,
    service: LeadService = Depends(get_lead_service),
):
    lead = await service.update_status(id, status_update.status)
    return success_response(
        data=LeadResponse.model_validate(lead),
        message="Lead status updated successfully",
    )


@router.post(
    "/{id}/follow-up",
    response_model=SuccessResponse[LeadResponse],
    summary="Add follow-up notes to a lead",
)
async def follow_up_lead(
    id: UUID,
    follow_up: LeadFollowUpUpdate,
    service: LeadService = Depends(get_lead_service),
):
    lead = await service.record_follow_up(id, follow_up.notes)
    return success_response(
        data=LeadResponse.model_validate(lead),
        message="Follow-up recorded successfully",
    )


@router.get(
    "/student/{student_id}",
    response_model=SuccessResponse[list[LeadResponse]],
    summary="Get leads by student ID",
)
async def get_leads_by_student(
    student_id: UUID, service: LeadService = Depends(get_lead_service)
):
    leads = await service.get_by_student(student_id)
    data = [LeadResponse.model_validate(l) for l in leads]
    return success_response(data=data, message="Leads retrieved successfully")
