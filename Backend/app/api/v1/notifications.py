from uuid import UUID

from fastapi import APIRouter, Depends

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_notification_service
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get(
    "",
    response_model=SuccessResponse[list[NotificationResponse]],
    summary="Get current user's notifications",
)
async def list_notifications(
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service),
):
    notifications = await service.list_notifications(current_user)
    data = [NotificationResponse.model_validate(n) for n in notifications]
    return success_response(data=data, message="Notifications retrieved successfully")


@router.patch(
    "/{id}/read",
    response_model=SuccessResponse[NotificationResponse],
    summary="Mark a notification as read",
)
async def mark_as_read(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service),
):
    notification = await service.mark_as_read(id, current_user)
    return success_response(
        data=NotificationResponse.model_validate(notification),
        message="Notification marked as read",
    )


@router.post(
    "/read-all",
    response_model=SuccessResponse,
    summary="Mark all notifications as read",
)
async def mark_all_read(
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service),
):
    await service.mark_all_read(current_user)
    return success_response(message="All notifications marked as read")


@router.delete(
    "/{id}",
    response_model=SuccessResponse,
    summary="Delete a notification",
)
async def delete_notification(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service),
):
    await service.delete_notification(id, current_user)
    return success_response(message="Notification deleted successfully")
