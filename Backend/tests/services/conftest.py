import pytest
from unittest.mock import MagicMock
from app.repositories.transaction import TransactionManager

@pytest.fixture
def mock_transaction_manager():
    tm = MagicMock(spec=TransactionManager)
    
    class AsyncContextManagerMock:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                return False
            return True

    tm.transaction.return_value = AsyncContextManagerMock()
    return tm
