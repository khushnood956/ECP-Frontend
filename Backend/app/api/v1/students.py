from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_student_service
from app.models.user import User
from app.repositories.params import PaginationParams
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services.student_service import StudentService

router = APIRouter()

@router.post(
    "",
    response_model=SuccessResponse[StudentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a student profile",
)
async def create_student(
    student_in: StudentCreate, 
    current_user: User = Depends(get_current_active_user),
    service: StudentService = Depends(get_student_service)
):
    student = await service.create(student_in, current_user)
    return success_response(
        data=StudentResponse.model_validate(student),
        message="Student created successfully",
        status_code=201,
    )


@router.get(
    "/{id}",
    response_model=SuccessResponse[StudentResponse],
    summary="Get a student profile by ID",
)
async def get_student(
    id: UUID, 
    current_user: User = Depends(get_current_active_user),
    service: StudentService = Depends(get_student_service)
):
    student = await service.get_by_id_scoped(id, current_user)
    if not student:
        from app.services.exceptions import EntityNotFound
        raise EntityNotFound(f"Student profile with id {id} not found.")
        
    return success_response(
        data=StudentResponse.model_validate(student),
        message="Student retrieved successfully",
    )


@router.get(
    "",
    response_model=SuccessResponse[list[StudentResponse]],
    summary="Get all student profiles",
)
async def get_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: StudentService = Depends(get_student_service),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    paginated_result = await service.list_student_profiles(current_user, pagination)
    data = [StudentResponse.model_validate(s) for s in paginated_result.items]
    return success_response(data=data, message="Students retrieved successfully")


@router.patch(
    "/{id}",
    response_model=SuccessResponse[StudentResponse],
    summary="Update a student profile",
)
async def update_student(
    id: UUID,
    student_in: StudentUpdate,
    current_user: User = Depends(get_current_active_user),
    service: StudentService = Depends(get_student_service),
):
    target_id = id
    # Resolve user_id to profile_id if needed
    student = await service.get_by_id(id)
    if not student:
        student = await service.get_by_user_id(id)
        if student:
            target_id = UUID(student.id)
            
    student = await service.update(target_id, student_in, current_user)
    return success_response(
        data=StudentResponse.model_validate(student),
        message="Student updated successfully",
    )


@router.delete(
    "/{id}", 
    response_model=None, 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student profile"
)
async def delete_student(
    id: UUID, 
    current_user: User = Depends(get_current_active_user),
    service: StudentService = Depends(get_student_service)
):
    target_id = id
    # BaseService.delete will raise EntityNotFound if not exists
    student = await service.get_by_id(id)
    if not student:
        student = await service.get_by_user_id(id)
        if student:
            target_id = UUID(student.id)
            
    await service.delete(target_id, current_user)
