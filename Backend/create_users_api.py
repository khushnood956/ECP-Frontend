import os

with open('app/schemas/user.py', 'w') as f:
    f.write('''from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.STUDENT
    is_active: bool = True
    is_verified: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True

class PaginatedUserResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
''')

with open('app/api/v1/users.py', 'w') as f:
    f.write('''from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, status, Query, HTTPException

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.services import get_user_service
from app.schemas.user import UserCreate, UserResponse, UserUpdate, PaginatedUserResponse
from app.services.user_service import UserService
from app.repositories.params import PaginationParams, FilterCondition, FilterOperator
from app.models.enums import UserRole

router = APIRouter()

@router.get(
    "", response_model=SuccessResponse[PaginatedUserResponse], summary="Get all users (paginated)"
)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    email: Optional[str] = None,
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
async def get_user(id: UUID, service: UserService = Depends(get_user_service)):
    user = await service.get(id)
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
    id: UUID, user_in: UserUpdate, service: UserService = Depends(get_user_service)
):
    user = await service.update_user(id, user_in)
    return success_response(
        data=UserResponse.model_validate(user), message="User updated successfully"
    )

@router.delete("/{id}", response_model=SuccessResponse, summary="Deactivate a user")
async def delete_user(id: UUID, service: UserService = Depends(get_user_service)):
    # Soft delete (deactivate)
    from app.services.exceptions import BusinessRuleViolation, EntityNotFound
    try:
        await service.deactivate(id)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessRuleViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    return success_response(message="User deactivated successfully")

''')
