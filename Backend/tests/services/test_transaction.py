import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.user import User
from app.repositories.transaction import TransactionManager
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_transaction_boundary_success():
    """Verify successful commit execution inside TransactionManager."""
    tm = MagicMock(spec=TransactionManager)
    context_manager_mock = AsyncMock()
    tm.transaction.return_value = context_manager_mock

    user_repo = AsyncMock()
    user_id = uuid.uuid4()
    user_repo.get_by_id.return_value = User(id=user_id, is_active=False)

    service = UserService(repository=user_repo, transaction_manager=tm)
    await service.activate(user_id)

    # transaction method should be called
    tm.transaction.assert_called_once()
    # verify context manager entered and exited
    context_manager_mock.__aenter__.assert_called_once()
    context_manager_mock.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_transaction_rollback_on_exception():
    """Verify rollback on exception (exception propagates and context manager handles it)."""
    tm = MagicMock(spec=TransactionManager)
    context_manager_mock = AsyncMock()
    tm.transaction.return_value = context_manager_mock

    user_repo = AsyncMock()
    user_id = uuid.uuid4()
    user_repo.get_by_id.side_effect = Exception("Database error")

    service = UserService(repository=user_repo, transaction_manager=tm)

    with pytest.raises(Exception, match="Database error"):
        await service.activate(user_id)

    context_manager_mock.__aenter__.assert_called_once()
    context_manager_mock.__aexit__.assert_called_once()
