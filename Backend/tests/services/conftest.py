from unittest.mock import MagicMock

import pytest

from app.repositories.transaction import TransactionManager


@pytest.fixture
def mock_transaction_manager():
    tm = MagicMock(spec=TransactionManager)
    tm.session = MagicMock()

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return exc_type is None

    tm.transaction.return_value = AsyncContextManagerMock()
    return tm
