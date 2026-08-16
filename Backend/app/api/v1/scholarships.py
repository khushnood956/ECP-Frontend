from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_scholarship_service
from app.models.enums import DegreeLevel, FundingType, UserRole
from app.models.user import User
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipResponse,
    ScholarshipUpdate,
)
from app.services.exceptions import PermissionDenied
from app.services.scholarship_service import ScholarshipService

router = APIRouter()


def check_agency_or_admin_role(user: User):
    if user.role not in [UserRole.AGENCY, UserRole.ADMIN]:
        raise PermissionDenied("Only agency or admin users can perform this action.")


@router.post(
    "",
    response_model=SuccessResponse[ScholarshipResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a scholarship",
)
async def create_scholarship(
    scholarship_in: ScholarshipCreate,
    current_user: User = Depends(get_current_active_user),
    service: ScholarshipService = Depends(get_scholarship_service),
):
    scholarship = await service.create(scholarship_in, current_user)
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship created successfully",
        status_code=201,
    )


@router.get(
    "/active",
    response_model=SuccessResponse[list[ScholarshipResponse]],
    summary="Get active scholarships",
)
async def get_active_scholarships(
    current_user: User = Depends(get_current_active_user),
    service: ScholarshipService = Depends(get_scholarship_service),
):
    scholarships = await service.list_active_scoped(current_user)
    data = [ScholarshipResponse.model_validate(s) for s in scholarships]
    return success_response(
        data=data, message="Active scholarships retrieved successfully"
    )


@router.get(
    "/search",
    response_model=SuccessResponse[list[ScholarshipResponse]],
    summary="Search scholarships",
)
async def search_scholarships(
    country: str | None = None,
    degree_level: DegreeLevel | None = None,
    funding_type: FundingType | None = None,
    current_user: User = Depends(get_current_active_user),
    service: ScholarshipService = Depends(get_scholarship_service),
):
    kwargs = {}
    if country is not None:
        kwargs["country"] = country
    if degree_level is not None:
        kwargs["degree_level"] = degree_level
    if funding_type is not None:
        kwargs["funding_type"] = funding_type

    scholarships = await service.search(current_user, **kwargs)
    data = [ScholarshipResponse.model_validate(s) for s in scholarships]
    return success_response(data=data, message="Scholarships retrieved successfully")


@router.get(
    "/{id}",
    response_model=SuccessResponse[ScholarshipResponse],
    summary="Get a scholarship by ID",
)
async def get_scholarship(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ScholarshipService = Depends(get_scholarship_service),
):
    scholarship = await service.get_by_id(id, current_user)
    if not scholarship:
        from app.services.exceptions import EntityNotFound
        raise EntityNotFound(f"Scholarship with id {id} not found.")
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship retrieved successfully",
    )


@router.get(
    "",
    response_model=SuccessResponse[list[ScholarshipResponse]],
    summary="Get all scholarships",
)
async def get_scholarships(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: ScholarshipService = Depends(get_scholarship_service),
):
    from app.repositories.params import PaginationParams
    pagination = PaginationParams(page=page, page_size=page_size)
    paginated_result = await service.list_scholarships(current_user, pagination)
    data = [ScholarshipResponse.model_validate(s) for s in paginated_result.items]
    return success_response(data=data, message="Scholarships retrieved successfully")


@router.patch(
    "/{id}",
    response_model=SuccessResponse[ScholarshipResponse],
    summary="Update a scholarship",
)
async def update_scholarship(
    id: UUID,
    scholarship_in: ScholarshipUpdate,
    current_user: User = Depends(get_current_active_user),
    service: ScholarshipService = Depends(get_scholarship_service),
):
    scholarship = await service.update(id, scholarship_in, current_user)
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship updated successfully",
    )


@router.delete("/{id}", response_model=SuccessResponse, summary="Delete a scholarship")
async def delete_scholarship(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ScholarshipService = Depends(get_scholarship_service),
):
    await service.delete(id, current_user)
    return success_response(message="Scholarship deleted successfully")


@router.post(
    "/{id}/publish",
    response_model=SuccessResponse[ScholarshipResponse],
    summary="Publish a scholarship",
)
async def publish_scholarship(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ScholarshipService = Depends(get_scholarship_service),
):
    check_agency_or_admin_role(current_user)
    scholarship = await service.publish(id, current_user)
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship published successfully",
    )


@router.post(
    "/{id}/unpublish",
    response_model=SuccessResponse[ScholarshipResponse],
    summary="Unpublish a scholarship",
)
async def unpublish_scholarship(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ScholarshipService = Depends(get_scholarship_service),
):
    check_agency_or_admin_role(current_user)
    scholarship = await service.unpublish(id, current_user)
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship unpublished successfully",
    )
