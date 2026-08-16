from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.common.utils.responses import success_response
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_class_service
from app.models.user import User
from app.repositories.params import PaginationParams
from app.schemas.academic_class import ClassCreate, ClassResponse, ClassUpdate
from app.services.class_service import ClassService

router = APIRouter()


@router.post("", response_model=Any, status_code=201)
async def create_class(
    class_in: ClassCreate,
    current_user: User = Depends(get_current_active_user),
    service: ClassService = Depends(get_class_service),
):
    cls_obj = await service.create(class_in, current_user)
    return success_response(
        data=ClassResponse.model_validate(cls_obj),
        message="Class created successfully",
        status_code=201,
    )


@router.get("", response_model=Any)
async def get_classes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: ClassService = Depends(get_class_service),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    paginated_result = await service.list_classes(current_user, pagination)
    data = [ClassResponse.model_validate(c) for c in paginated_result.items]
    return success_response(data=data, message="Classes retrieved successfully")


@router.get("/{id}", response_model=Any)
async def get_class(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ClassService = Depends(get_class_service),
):
    cls_obj = await service.get_by_id_scoped(id, current_user)
    if not cls_obj:
        from app.services.exceptions import EntityNotFound
        raise EntityNotFound(f"Class with ID {id} not found.")
    return success_response(
        data=ClassResponse.model_validate(cls_obj), message="Class retrieved successfully"
    )


@router.patch("/{id}", response_model=Any)
async def update_class(
    id: UUID,
    class_in: ClassUpdate,
    current_user: User = Depends(get_current_active_user),
    service: ClassService = Depends(get_class_service),
):
    cls_obj = await service.update(id, class_in, current_user)
    return success_response(
        data=ClassResponse.model_validate(cls_obj), message="Class updated successfully"
    )


@router.delete("/{id}", status_code=204)
async def delete_class(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ClassService = Depends(get_class_service),
):
    await service.delete(id, current_user)
    return success_response(data=None, message="Class deleted successfully", status_code=204)


# Ensure typing/compilation doesn't fail on Any
from typing import Any
