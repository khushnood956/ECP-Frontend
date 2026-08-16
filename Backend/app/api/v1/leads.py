from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.auth import RequireRole, get_current_active_user
from app.dependencies.services import get_lead_service
from app.models.enums import LeadStatus, UserRole
from app.models.user import User
from app.schemas.lead import (
    LeadCreate,
    LeadPatchRequest,
    LeadResponse,
    LeadStatusUpdate,
)
from app.services.lead_service import LeadService

router = APIRouter()


@router.post(
    "",
    response_model=SuccessResponse[LeadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a lead (apply for scholarship)",
)
async def create_lead(
    lead_in: LeadCreate,
    current_user: User = Depends(get_current_active_user),
    service: LeadService = Depends(get_lead_service),
):
    lead = await service.create(lead_in, current_user)
    return success_response(
        data=LeadResponse.model_validate(lead),
        message="Lead created successfully",
        status_code=201,
    )


@router.get(
    "/{id}",
    response_model=SuccessResponse[LeadResponse],
    summary="Get a lead by ID",
)
async def get_lead(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: LeadService = Depends(get_lead_service),
):
    lead = await service.get_by_id(id, current_user)
    if not lead:
        from app.services.exceptions import EntityNotFound
        raise EntityNotFound(f"Lead with id {id} not found.")
    return success_response(
        data=LeadResponse.model_validate(lead),
        message="Lead retrieved successfully",
    )


@router.get(
    "",
    response_model=SuccessResponse[list[LeadResponse]],
    summary="Get all leads (scoped by role)",
)
async def get_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: LeadStatus | None = None,
    scholarship_id: UUID | None = None,
    current_user: User = Depends(get_current_active_user),
    service: LeadService = Depends(get_lead_service),
):
    from app.repositories.params import (
        FilterCondition,
        FilterOperator,
        PaginationParams,
    )
    pagination = PaginationParams(page=page, page_size=page_size)
    filters = []
    if status is not None:
        filters.append(FilterCondition(field="status", operator=FilterOperator.EQ, value=status))
    if scholarship_id is not None:
        filters.append(FilterCondition(field="scholarship_id", operator=FilterOperator.EQ, value=str(scholarship_id)))
    
    paginated_result = await service.list_leads(current_user, pagination, filters=filters)
    data = [LeadResponse.model_validate(l) for l in paginated_result.items]
    return success_response(data=data, message="Leads retrieved successfully")


@router.patch(
    "/{id}",
    response_model=SuccessResponse[LeadResponse],
    summary="Update a lead",
)
async def update_lead(
    id: UUID,
    lead_in: LeadPatchRequest,
    current_user: User = Depends(get_current_active_user),
    service: LeadService = Depends(get_lead_service),
):
    lead = await service.update(id, lead_in, current_user)
    return success_response(
        data=LeadResponse.model_validate(lead),
        message="Lead updated successfully",
    )


@router.delete(
    "/{id}",
    response_model=SuccessResponse,
    summary="Withdraw or delete a lead",
)
async def delete_lead(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: LeadService = Depends(get_lead_service),
):
    await service.delete(id, current_user)
    return success_response(message="Lead deleted successfully")


# --- Legacy endpoints preserved for backward compatibility ---

@router.post(
    "/{id}/assign-agency",
    response_model=SuccessResponse[LeadResponse],
    summary="Assign an agency to a lead",
    tags=["Admin"],
)
async def assign_agency(
    id: UUID,
    agency_id: UUID,
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    service: LeadService = Depends(get_lead_service),
):
    lead = await service.assign_agency(id, agency_id)
    return success_response(
        data=LeadResponse.model_validate(lead),
        message="Agency assigned successfully",
    )


@router.post(
    "/{id}/status",
    response_model=SuccessResponse[LeadResponse],
    summary="Update lead status",
    tags=["Admin"],
)
async def update_lead_status(
    id: UUID,
    status_update: LeadStatusUpdate,
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    service: LeadService = Depends(get_lead_service),
):
    # Mapping request string representation if needed
    status_map_rev = {
        "submitted": LeadStatus.NEW,
        "under_review": LeadStatus.CONTACTED,
        "accepted": LeadStatus.WON,
        "rejected": LeadStatus.LOST
    }
    target_status = status_map_rev.get(status_update.status, LeadStatus.NEW)
    lead = await service.update_status(id, target_status)
    return success_response(
        data=LeadResponse.model_validate(lead),
        message="Lead status updated successfully",
    )


@router.get(
    "/student/{student_id}",
    response_model=SuccessResponse[list[LeadResponse]],
    summary="Get leads by student ID",
)
async def get_leads_by_student(
    student_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: LeadService = Depends(get_lead_service),
):
    leads = await service.leads_by_student(student_id, current_user)
    data = [LeadResponse.model_validate(l) for l in leads]
    return success_response(data=data, message="Leads retrieved successfully")
