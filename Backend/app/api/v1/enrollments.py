from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.common.utils.responses import success_response
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_enrollment_service
from app.models.user import User
from app.repositories.params import PaginationParams
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentUpdate,
)
from app.services.enrollment_service import EnrollmentService

router = APIRouter()


@router.post("", response_model=Any, status_code=201)
async def create_enrollment(
    enrollment_in: EnrollmentCreate,
    current_user: User = Depends(get_current_active_user),
    service: EnrollmentService = Depends(get_enrollment_service),
):
    enrollment = await service.create(enrollment_in, current_user)
    return success_response(
        data=EnrollmentResponse.model_validate(enrollment),
        message="Enrollment created successfully",
        status_code=201,
    )


@router.get("", response_model=Any)
async def get_enrollments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: EnrollmentService = Depends(get_enrollment_service),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    paginated_result = await service.list_enrollments(current_user, pagination)
    data = [EnrollmentResponse.model_validate(e) for e in paginated_result.items]
    return success_response(data=data, message="Enrollments retrieved successfully")


@router.get("/{id}", response_model=Any)
async def get_enrollment(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: EnrollmentService = Depends(get_enrollment_service),
):
    enrollment = await service.get_by_id_scoped(id, current_user)
    if not enrollment:
        from app.services.exceptions import EntityNotFound
        raise EntityNotFound(f"Enrollment with ID {id} not found.")
    return success_response(
        data=EnrollmentResponse.model_validate(enrollment),
        message="Enrollment retrieved successfully",
    )


@router.patch("/{id}", response_model=Any)
async def update_enrollment(
    id: UUID,
    enrollment_in: EnrollmentUpdate,
    current_user: User = Depends(get_current_active_user),
    service: EnrollmentService = Depends(get_enrollment_service),
):
    enrollment = await service.update(id, enrollment_in, current_user)
    return success_response(
        data=EnrollmentResponse.model_validate(enrollment),
        message="Enrollment updated successfully",
    )


@router.delete("/{id}", status_code=204)
async def delete_enrollment(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: EnrollmentService = Depends(get_enrollment_service),
):
    await service.delete(id, current_user)
    return success_response(data=None, message="Enrollment deleted successfully", status_code=204)
