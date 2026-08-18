from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.auth import RequireRole
from app.dependencies.services import get_bookmark_service
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.bookmark import BookmarkCreate, BookmarkResponse
from app.services.bookmark_service import BookmarkService

router = APIRouter()


@router.get(
    "",
    response_model=SuccessResponse[list[BookmarkResponse]],
    summary="Get current student's bookmarks",
)
async def list_bookmarks(
    current_user: User = Depends(RequireRole([UserRole.STUDENT])),
    service: BookmarkService = Depends(get_bookmark_service),
):
    bookmarks = await service.list_bookmarks(current_user)
    data = [BookmarkResponse.model_validate(b) for b in bookmarks]
    return success_response(data=data, message="Bookmarks retrieved successfully")


@router.post(
    "",
    response_model=SuccessResponse[BookmarkResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bookmark",
)
async def create_bookmark(
    bookmark_in: BookmarkCreate,
    current_user: User = Depends(RequireRole([UserRole.STUDENT])),
    service: BookmarkService = Depends(get_bookmark_service),
):
    bookmark = await service.create_bookmark(
        bookmark_type=bookmark_in.bookmark_type,
        scholarship_id=bookmark_in.scholarship_id,
        university_id=bookmark_in.university_id,
        current_user=current_user,
    )
    return success_response(
        data=BookmarkResponse.model_validate(bookmark),
        message="Bookmark created successfully",
        status_code=201,
    )


@router.delete("/{id}", response_model=SuccessResponse, summary="Remove a bookmark")
async def delete_bookmark(
    id: UUID,
    current_user: User = Depends(RequireRole([UserRole.STUDENT])),
    service: BookmarkService = Depends(get_bookmark_service),
):
    await service.delete_bookmark(id, current_user)
    return success_response(message="Bookmark deleted successfully")
