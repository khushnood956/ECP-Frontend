import pytest
import uuid
from unittest.mock import AsyncMock
from app.services.student_service import StudentService
from app.services.exceptions import EntityNotFound

@pytest.fixture
def student_repo_mock():
    return AsyncMock()

@pytest.fixture
def student_service(student_repo_mock, mock_transaction_manager):
    return StudentService(repository=student_repo_mock, transaction_manager=mock_transaction_manager)

@pytest.mark.asyncio
async def test_update_profile_not_found(student_service, student_repo_mock):
    user_id = uuid.uuid4()
    student_repo_mock.get_by_user_id.return_value = None

    with pytest.raises(EntityNotFound, match="not found"):
        await student_service.update_profile(user_id, {"some": "data"})
