from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.common.utils.responses import success_response
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_attendance_service
from app.models.user import User
from app.repositories.params import PaginationParams
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
)
from app.services.attendance_service import AttendanceService

router = APIRouter()


@router.post("", response_model=Any, status_code=201)
async def create_attendance(
    attendance_in: AttendanceCreate,
    current_user: User = Depends(get_current_active_user),
    service: AttendanceService = Depends(get_attendance_service),
):
    attendance = await service.create(attendance_in, current_user)
    return success_response(
        data=AttendanceResponse.model_validate(attendance),
        message="Attendance recorded successfully",
        status_code=201,
    )


@router.get("", response_model=Any)
async def get_attendances(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: AttendanceService = Depends(get_attendance_service),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    paginated_result = await service.list_attendance(current_user, pagination)
    data = [AttendanceResponse.model_validate(a) for a in paginated_result.items]
    return success_response(data=data, message="Attendance records retrieved successfully")


@router.get("/{id}", response_model=Any)
async def get_attendance(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: AttendanceService = Depends(get_attendance_service),
):
    attendance = await service.get_by_id_scoped(id, current_user)
    if not attendance:
        from app.services.exceptions import EntityNotFound
        raise EntityNotFound(f"Attendance with ID {id} not found.")
    return success_response(
        data=AttendanceResponse.model_validate(attendance),
        message="Attendance record retrieved successfully",
    )


@router.patch("/{id}", response_model=Any)
async def update_attendance(
    id: UUID,
    attendance_in: AttendanceUpdate,
    current_user: User = Depends(get_current_active_user),
    service: AttendanceService = Depends(get_attendance_service),
):
    attendance = await service.update(id, attendance_in, current_user)
    return success_response(
        data=AttendanceResponse.model_validate(attendance),
        message="Attendance record updated successfully",
    )


@router.delete("/{id}", status_code=204)
async def delete_attendance(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: AttendanceService = Depends(get_attendance_service),
):
    await service.delete(id, current_user)
    return success_response(data=None, message="Attendance record deleted successfully", status_code=204)
