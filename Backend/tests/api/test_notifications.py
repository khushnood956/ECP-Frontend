from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import UserRole
from app.models.user import User
from main import app

TEST_STUDENT_USER_ID = str(uuid4())

def _student_user():
    return User(id=TEST_STUDENT_USER_ID, email="student@test.com", is_active=True, role=UserRole.STUDENT)

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_active_user] = _student_user
    yield
    app.dependency_overrides.clear()

class MockNotification:
    def __init__(self, notification_id=None, user_id=None):
        self.id = notification_id or uuid4()
        self.user_id = user_id or uuid4()
        self.title = "Test Notif"
        self.message = "Hello World"
        self.is_read = False
        self.related_entity_id = uuid4()
        self.created_at = "2026-08-17T22:11:00Z"
        self.updated_at = "2026-08-17T22:11:00Z"

@pytest.mark.asyncio
async def test_list_notifications_success():
    with patch('app.services.notification_service.NotificationService.list_notifications', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [MockNotification(user_id=TEST_STUDENT_USER_ID)]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/notifications")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

@pytest.mark.asyncio
async def test_mark_as_read_success():
    with patch('app.services.notification_service.NotificationService.mark_as_read', new_callable=AsyncMock) as mock_read:
        notif = MockNotification(user_id=TEST_STUDENT_USER_ID)
        notif.is_read = True
        mock_read.return_value = notif
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/notifications/{notif.id}/read")
        assert response.status_code == 200
        assert response.json()["data"]["is_read"] is True

@pytest.mark.asyncio
async def test_mark_all_read_success():
    with patch('app.services.notification_service.NotificationService.mark_all_read', new_callable=AsyncMock) as mock_all_read:
        mock_all_read.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/notifications/read-all")
        assert response.status_code == 200
        assert response.json()["message"] == "All notifications marked as read"

@pytest.mark.asyncio
async def test_delete_notification_success():
    with patch('app.services.notification_service.NotificationService.delete_notification', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        notif_id = uuid4()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/notifications/{notif_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Notification deleted successfully"
