from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_university_service
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.university import (
    UniversityCreate,
    UniversityResponse,
)
from app.services.exceptions import EntityNotFound, PermissionDenied
from app.services.university_service import UniversityService

router = APIRouter()


def check_admin_role(user: User):
    if user.role != UserRole.ADMIN:
        raise PermissionDenied("Only admin users can perform this action.")


@router.post(
    "",
    response_model=SuccessResponse[UniversityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a university",
)
async def create_university(
    university_in: UniversityCreate,
    current_user: User = Depends(get_current_active_user),
    service: UniversityService = Depends(get_university_service),
):
    check_admin_role(current_user)
    # Convert Pydantic object to model instance
    uni_model = service._to_model(university_in)
    async with service.transaction_manager.transaction():
        created_uni = await service.repository.create(uni_model)
    return success_response(
        data=UniversityResponse.model_validate(created_uni),
        message="University created successfully",
        status_code=201,
    )


@router.get(
    "/search",
    response_model=SuccessResponse[list[UniversityResponse]],
    summary="Search universities",
)
async def search_universities(
    name: str | None = None,
    location: str | None = None,
    current_user: User = Depends(get_current_active_user),
    service: UniversityService = Depends(get_university_service),
):
    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if location is not None:
        kwargs["location"] = location

    unis = await service.search(**kwargs)
    data = [UniversityResponse.model_validate(u) for u in unis]
    return success_response(data=data, message="Universities retrieved successfully")


@router.get(
    "/{id}",
    response_model=SuccessResponse[UniversityResponse],
    summary="Get a university by ID",
)
async def get_university(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UniversityService = Depends(get_university_service),
):
    uni = await service.get_by_id(id)
    if not uni:
        raise EntityNotFound(f"University with id {id} not found.")
    return success_response(
        data=UniversityResponse.model_validate(uni),
        message="University retrieved successfully",
    )


@router.get(
    "",
    response_model=SuccessResponse[list[UniversityResponse]],
    summary="Get all universities",
)
async def get_universities(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: UniversityService = Depends(get_university_service),
):
    from app.repositories.params import PaginationParams
    pagination = PaginationParams(page=page, page_size=page_size)
    paginated_result = await service.list_universities(pagination)
    data = [UniversityResponse.model_validate(u) for u in paginated_result.items]
    return success_response(data=data, message="Universities retrieved successfully")


@router.delete("/{id}", response_model=SuccessResponse, summary="Delete a university")
async def delete_university(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UniversityService = Depends(get_university_service),
):
    check_admin_role(current_user)
    await service._require_entity(id)
    async with service.transaction_manager.transaction():
        await service.repository.delete(id)
    return success_response(message="University deleted successfully")
