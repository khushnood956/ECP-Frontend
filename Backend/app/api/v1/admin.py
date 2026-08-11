from fastapi import APIRouter, Depends

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.auth import RequireRole
from app.dependencies.services import get_admin_service
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.admin import DashboardStatistics
from app.services.admin_service import AdminService

router = APIRouter()

@router.get(
    "/statistics",
    response_model=SuccessResponse[DashboardStatistics],
    summary="Get admin dashboard statistics",
)
async def get_dashboard_statistics(
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    service: AdminService = Depends(get_admin_service),
):
    stats = await service.get_dashboard_statistics()
    return success_response(data=stats, message="Statistics retrieved successfully")
