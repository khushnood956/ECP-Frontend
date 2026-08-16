from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.admin import DashboardStatistics
from main import app


def override_get_current_admin_user():
    return User(id="admin-id", email="admin@test.com", is_active=True, role=UserRole.ADMIN)

def override_get_current_student_user():
    return User(id="student-id", email="student@test.com", is_active=True, role=UserRole.STUDENT)

@pytest.fixture
def setup_admin_override():
    app.dependency_overrides[get_current_active_user] = override_get_current_admin_user
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_dashboard_statistics(setup_admin_override):
    mock_stats = DashboardStatistics(
        total_users=10,
        total_students=5,
        total_agencies=2,
        verified_agencies=1,
        pending_agencies=1,
        suspended_agencies=0,
        active_scholarships=5,
        total_leads=10,
        leads_new=2,
        leads_contacted=2,
        leads_won=4,
        leads_lost=2
    )

    with patch('app.services.admin_service.AdminService.get_dashboard_statistics', new_callable=AsyncMock) as mock_get_stats:
        mock_get_stats.return_value = mock_stats

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/admin/statistics")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_users"] == 10
        assert data["active_scholarships"] == 5

@pytest.mark.asyncio
async def test_get_dashboard_statistics_forbidden():
    app.dependency_overrides[get_current_active_user] = override_get_current_student_user
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/admin/statistics")

    assert response.status_code == 403
    app.dependency_overrides.clear()
