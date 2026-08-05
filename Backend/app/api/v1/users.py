from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.services import get_user_service
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    # Note: normally we would hash the password here or in auth service, but keeping it simple for CRUD.
    # Service layer is expected to handle the creation.
    user = await service.create(user_in)
    return success_response(
        data=UserResponse.model_validate(user),
        message="User created successfully",
        status_code=201,
    )


@router.get(
    "/{id}", response_model=SuccessResponse[UserResponse], summary="Get a user by ID"
)
async def get_user(id: UUID, service: UserService = Depends(get_user_service)):
    user = await service.get(id)
    return success_response(
        data=UserResponse.model_validate(user), message="User retrieved successfully"
    )


@router.get(
    "", response_model=SuccessResponse[list[UserResponse]], summary="Get all users"
)
async def get_users(
    skip: int = 0, limit: int = 100, service: UserService = Depends(get_user_service)
):
    users, total = await service.get_all(skip=skip, limit=limit)
    data = [UserResponse.model_validate(u) for u in users]
    return success_response(data=data, message="Users retrieved successfully")


@router.patch(
    "/{id}", response_model=SuccessResponse[UserResponse], summary="Update a user"
)
async def update_user(
    id: UUID, user_in: UserUpdate, service: UserService = Depends(get_user_service)
):
    user = await service.update(id, user_in)
    return success_response(
        data=UserResponse.model_validate(user), message="User updated successfully"
    )


@router.delete("/{id}", response_model=SuccessResponse, summary="Delete a user")
async def delete_user(id: UUID, service: UserService = Depends(get_user_service)):
    await service.delete(id)
    return success_response(message="User deleted successfully")


@router.post(
    "/{id}/activate",
    response_model=SuccessResponse[UserResponse],
    summary="Activate a user",
)
async def activate_user(id: UUID, service: UserService = Depends(get_user_service)):
    user = await service.activate(id)
    return success_response(
        data=UserResponse.model_validate(user), message="User activated successfully"
    )


@router.post(
    "/{id}/deactivate",
    response_model=SuccessResponse[UserResponse],
    summary="Deactivate a user",
)
async def deactivate_user(id: UUID, service: UserService = Depends(get_user_service)):
    user = await service.deactivate(id)
    return success_response(
        data=UserResponse.model_validate(user), message="User deactivated successfully"
    )


@router.get(
    "/email/{email}",
    response_model=SuccessResponse[UserResponse],
    summary="Get a user by email",
)
async def get_user_by_email(
    email: str, service: UserService = Depends(get_user_service)
):
    user = await service.get_by_email(email)
    if not user:
        from app.services.exceptions import EntityNotFound

        raise EntityNotFound(f"User with email {email} not found.")
    return success_response(
        data=UserResponse.model_validate(user), message="User retrieved successfully"
    )
