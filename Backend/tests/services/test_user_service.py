import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.user import User
from app.services.exceptions import BusinessRuleViolation
from app.services.user_service import UserService


@pytest.fixture
def user_repo_mock():
    return AsyncMock()


@pytest.fixture
def user_service(user_repo_mock, mock_transaction_manager):
    return UserService(
        repository=user_repo_mock, transaction_manager=mock_transaction_manager
    )


@pytest.mark.asyncio
async def test_activate_success(user_service, user_repo_mock):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, is_active=False)
    user_repo_mock.get_by_id.return_value = mock_user
    user_repo_mock.update.return_value = User(id=user_id, is_active=True)

    result = await user_service.activate(user_id)
    assert result.is_active is True
    user_repo_mock.update.assert_called_once_with(user_id, {"is_active": True})


@pytest.mark.asyncio
async def test_activate_twice_fails(user_service, user_repo_mock):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, is_active=True)
    user_repo_mock.get_by_id.return_value = mock_user

    with pytest.raises(BusinessRuleViolation, match="already active"):
        await user_service.activate(user_id)


@pytest.mark.asyncio
async def test_deactivate_twice_fails(user_service, user_repo_mock):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, is_active=False)
    user_repo_mock.get_by_id.return_value = mock_user

    with pytest.raises(BusinessRuleViolation, match="already inactive"):
        await user_service.deactivate(user_id)
