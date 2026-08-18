from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.enums import UserRole
from app.models.notification import Notification
from app.services.exceptions import PermissionDenied
from app.services.notification_service import NotificationService


class MockUser:
    def __init__(self, role=UserRole.STUDENT):
        self.id = uuid4()
        self.email = "student@test.com"
        self.role = role

@pytest.mark.asyncio
async def test_service_create_notification_success():
    repo = AsyncMock()
    tx_manager = MagicMock()
    tx_context = AsyncMock()
    tx_manager.transaction.return_value = tx_context

    service = NotificationService(repository=repo, transaction_manager=tx_manager)
    
    user = MockUser()
    repo.create.return_value = Notification(
        id=uuid4(),
        user_id=str(user.id),
        title="App Submitted",
        message="Your application is success."
    )

    result = await service.create_notification(
        user_id=user.id,
        title="App Submitted",
        message="Your application is success."
    )
    assert result is not None
    repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_service_mark_read_idor_protection():
    repo = AsyncMock()
    tx_manager = MagicMock()

    service = NotificationService(repository=repo, transaction_manager=tx_manager)
    
    user = MockUser()
    # Notification belongs to someone else
    other_user_id = uuid4()
    notif = Notification(
        id=uuid4(),
        user_id=str(other_user_id),
        title="Alert",
        message="Update status",
        is_read=False
    )
    repo.get_by_id.return_value = notif

    with pytest.raises(PermissionDenied) as exc:
        await service.mark_as_read(notif.id, user)
    assert "permission" in str(exc.value)

@pytest.mark.asyncio
async def test_service_delete_idor_protection():
    repo = AsyncMock()
    tx_manager = MagicMock()

    service = NotificationService(repository=repo, transaction_manager=tx_manager)
    
    user = MockUser()
    # Notification belongs to someone else
    other_user_id = uuid4()
    notif = Notification(
        id=uuid4(),
        user_id=str(other_user_id),
        title="Alert",
        message="Update status",
        is_read=False
    )
    repo.get_by_id.return_value = notif

    with pytest.raises(PermissionDenied) as exc:
        await service.delete_notification(notif.id, user)
    assert "permission" in str(exc.value)
