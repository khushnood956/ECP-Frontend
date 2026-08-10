from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.auth import RequireRole, get_current_active_user
from app.dependencies.services import get_user_service
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.params import FilterCondition, FilterOperator, PaginationParams
from app.schemas.user import PaginatedUserResponse, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

@router.get(
    "", response_model=SuccessResponse[PaginatedUserResponse], summary="Get all users (paginated)", tags=["Admin"]
)
async def get_users(
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role: UserRole | None = None,
    is_active: bool | None = None,
    email: str | None = None,
    service: UserService = Depends(get_user_service)
):
    pagination = PaginationParams(page=page, page_size=page_size)
    filters = []
    if role is not None:
        filters.append(FilterCondition(field="role", operator=FilterOperator.EQ, value=role))
    if is_active is not None:
        filters.append(FilterCondition(field="is_active", operator=FilterOperator.EQ, value=is_active))
    if email is not None:
        filters.append(FilterCondition(field="email", operator=FilterOperator.LIKE, value=email))
        
    paginated_result = await service.repository.list_paginated(pagination=pagination, filters=filters)
    data = PaginatedUserResponse(
        items=[UserResponse.model_validate(u) for u in paginated_result.items],
        total=paginated_result.total,
        page=paginated_result.page,
        page_size=paginated_result.page_size,
        total_pages=paginated_result.total_pages
    )
    return success_response(data=data, message="Users retrieved successfully")

@router.get(
    "/{id}", response_model=SuccessResponse[UserResponse], summary="Get a user by ID"
)
async def get_user(id: UUID, current_user: User = Depends(get_current_active_user), service: UserService = Depends(get_user_service)):
    if current_user.role != UserRole.ADMIN and str(current_user.id) != str(id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = await service.get_by_id(id)
    if not user:
        from app.services.exceptions import EntityNotFound
        raise EntityNotFound(f"User with ID {id} not found.")
    return success_response(
        data=UserResponse.model_validate(user), message="User retrieved successfully"
    )

@router.patch(
    "/{id}", response_model=SuccessResponse[UserResponse], summary="Update a user"
)
async def update_user(
    id: UUID, user_in: UserUpdate, current_user: User = Depends(get_current_active_user), service: UserService = Depends(get_user_service)
):
    user = await service.update(id, user_in, current_user)
    return success_response(
        data=UserResponse.model_validate(user), message="User updated successfully"
    )

@router.delete("/{id}", response_model=SuccessResponse, summary="Deactivate a user", tags=["Admin"])
async def delete_user(id: UUID, current_user: User = Depends(RequireRole([UserRole.ADMIN])), service: UserService = Depends(get_user_service)):
    from app.services.exceptions import EntityNotFound
    try:
        await service.delete(id, current_user)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return success_response(message="User deleted successfully")