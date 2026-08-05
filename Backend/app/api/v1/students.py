from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.services import get_student_service
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
    student_in: StudentCreate, service: StudentService = Depends(get_student_service)
):
    student = await service.create(student_in)
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
async def get_student(id: UUID, service: StudentService = Depends(get_student_service)):
    student = await service.get(id)
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
    skip: int = 0,
    limit: int = 100,
    service: StudentService = Depends(get_student_service),
):
    students, total = await service.get_all(skip=skip, limit=limit)
    data = [StudentResponse.model_validate(s) for s in students]
    return success_response(data=data, message="Students retrieved successfully")


@router.patch(
    "/{id}",
    response_model=SuccessResponse[StudentResponse],
    summary="Update a student profile",
)
async def update_student(
    id: UUID,
    student_in: StudentUpdate,
    service: StudentService = Depends(get_student_service),
):
    student = await service.update(id, student_in)
    return success_response(
        data=StudentResponse.model_validate(student),
        message="Student updated successfully",
    )


@router.delete(
    "/{id}", response_model=SuccessResponse, summary="Delete a student profile"
)
async def delete_student(
    id: UUID, service: StudentService = Depends(get_student_service)
):
    await service.delete(id)
    return success_response(message="Student deleted successfully")


@router.get(
    "/user/{user_id}",
    response_model=SuccessResponse[StudentResponse],
    summary="Get a student profile by User ID",
)
async def get_student_by_user_id(
    user_id: UUID, service: StudentService = Depends(get_student_service)
):
    student = await service.get_by_user_id(user_id)
    if not student:
        from app.services.exceptions import EntityNotFound

        raise EntityNotFound(f"Student profile for user {user_id} not found.")
    return success_response(
        data=StudentResponse.model_validate(student),
        message="Student retrieved successfully",
    )
