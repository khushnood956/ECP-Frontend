from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.auth import RequireRole, get_current_active_user
from app.dependencies.services import get_agency_service
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.agency import AgencyCreate, AgencyResponse, AgencyUpdate
from app.services.agency_service import AgencyService

router = APIRouter()


@router.post(
    "",
    response_model=SuccessResponse[AgencyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create an agency",
)
async def create_agency(
    agency_in: AgencyCreate,
    current_user: User = Depends(get_current_active_user),
    service: AgencyService = Depends(get_agency_service),
):
    agency = await service.create(agency_in, current_user)
    return success_response(
        data=AgencyResponse.model_validate(agency),
        message="Agency created successfully",
        status_code=201,
    )



@router.get(
    "/me",
    response_model=SuccessResponse[AgencyResponse],
    summary="Get current user's agency profile",
)
async def get_my_agency(
    current_user: User = Depends(get_current_active_user),
    service: AgencyService = Depends(get_agency_service),
):
    agency = await service.get_by_user_id(current_user.id, current_user)
    if not agency:
        from app.services.exceptions import EntityNotFound
        raise EntityNotFound(f"Agency profile for user {current_user.id} not found.")

    return success_response(
        data=AgencyResponse.model_validate(agency),
        message="Agency retrieved successfully",
    )



@router.get(
    "/{id}",
    response_model=SuccessResponse[AgencyResponse],
    summary="Get an agency by ID",
)
async def get_agency(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: AgencyService = Depends(get_agency_service),
):
    agency = await service.get_by_id(id, current_user)
    if not agency and hasattr(service, 'get_by_user_id'):
        agency = await service.get_by_user_id(id, current_user)
            
    if not agency:
        from app.services.exceptions import EntityNotFound
        raise EntityNotFound(f"Agency with id {id} not found.")

    return success_response(
        data=AgencyResponse.model_validate(agency),
        message="Agency retrieved successfully",
    )


@router.get(
    "",
    response_model=SuccessResponse[list[AgencyResponse]],
    summary="Get all agencies",
)
async def get_agencies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    verification_status: str | None = None,
    current_user: User = Depends(get_current_active_user),
    service: AgencyService = Depends(get_agency_service),
):
    from app.models.enums import AgencyVerificationStatus
    if current_user.role != UserRole.ADMIN:
        verification_status = AgencyVerificationStatus.VERIFIED
    elif verification_status:
        try:
            verification_status = AgencyVerificationStatus(verification_status)
        except ValueError:
            verification_status = None

    kwargs = {}
    if verification_status:
        kwargs["verification_status"] = verification_status

    agencies = await service.list(skip=skip, limit=limit, **kwargs)
    data = [AgencyResponse.model_validate(a) for a in agencies]
    return success_response(data=data, message="Agencies retrieved successfully")


@router.patch(
    "/{id}",
    response_model=SuccessResponse[AgencyResponse],
    summary="Update an agency",
)
async def update_agency(
    id: UUID,
    agency_in: AgencyUpdate,
    current_user: User = Depends(get_current_active_user),
    service: AgencyService = Depends(get_agency_service),
):
    target_id = id
    agency = await service.get_by_id(id, current_user)
    if not agency and hasattr(service, 'get_by_user_id'):
        agency = await service.get_by_user_id(id, current_user)
        if agency:
            target_id = UUID(agency.id)
                
    agency = await service.update(target_id, agency_in, current_user)
    return success_response(
        data=AgencyResponse.model_validate(agency),
        message="Agency updated successfully",
    )


@router.delete("/{id}", response_model=SuccessResponse, summary="Delete an agency")
async def delete_agency(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: AgencyService = Depends(get_agency_service),
):
    target_id = id
    agency = await service.get_by_id(id, current_user)
    if not agency and hasattr(service, 'get_by_user_id'):
        agency = await service.get_by_user_id(id, current_user)
        if agency:
            target_id = UUID(agency.id)
                
    await service.delete(target_id, current_user)
    return success_response(message="Agency deleted successfully")


@router.post(
    "/{id}/verify",
    response_model=SuccessResponse[AgencyResponse],
    summary="Verify an agency",
    tags=["Admin"],
)
async def verify_agency(
    id: UUID,
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    service: AgencyService = Depends(get_agency_service),
):
    target_id = id
    agency = await service.get_by_id(id, current_user)
    if not agency and hasattr(service, 'get_by_user_id'):
        agency = await service.get_by_user_id(id, current_user)
        if agency:
            target_id = UUID(agency.id)
                
    agency = await service.verify_agency(target_id)
    return success_response(
        data=AgencyResponse.model_validate(agency),
        message="Agency verified successfully",
    )


@router.post(
    "/{id}/suspend",
    response_model=SuccessResponse[AgencyResponse],
    summary="Suspend an agency",
    tags=["Admin"],
)
async def suspend_agency(
    id: UUID,
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    service: AgencyService = Depends(get_agency_service),
):
    target_id = id
    agency = await service.get_by_id(id, current_user)
    if not agency and hasattr(service, 'get_by_user_id'):
        agency = await service.get_by_user_id(id, current_user)
        if agency:
            target_id = UUID(agency.id)
                
    agency = await service.suspend_agency(target_id)
    return success_response(
        data=AgencyResponse.model_validate(agency),
        message="Agency suspended successfully",
    )


@router.get(
    "/registration/{registration_number}",
    response_model=SuccessResponse[AgencyResponse],
    summary="Get an agency by registration number",
)
async def get_agency_by_registration(
    registration_number: str,
    current_user: User = Depends(get_current_active_user),
    service: AgencyService = Depends(get_agency_service),
):
    agency = await service.get_by_registration_number(registration_number, current_user)
    if not agency:
        from app.services.exceptions import EntityNotFound

        raise EntityNotFound(
            f"Agency with registration number {registration_number} not found."
        )
    return success_response(
        data=AgencyResponse.model_validate(agency),
        message="Agency retrieved successfully",
    )

