import uuid
from unittest.mock import AsyncMock

import pytest

from app.services.exceptions import EntityNotFound
from app.services.student_service import StudentService


@pytest.fixture
def student_repo_mock():
    return AsyncMock()


@pytest.fixture
def student_service(student_repo_mock, mock_transaction_manager):
    return StudentService(
        repository=student_repo_mock, transaction_manager=mock_transaction_manager
    )


@pytest.mark.asyncio
async def test_update_profile_not_found(student_service, student_repo_mock):
    user_id = uuid.uuid4()
    student_repo_mock.get_by_user_id.return_value = None

    with pytest.raises(EntityNotFound, match="not found"):
        await student_service.update_profile(user_id, {"some": "data"})

from app.services.exceptions import BusinessRuleViolation


@pytest.mark.asyncio
async def test_create_student_success(student_service, student_repo_mock):
    user_id = uuid.uuid4()
    student_data = {"user_id": user_id}
    student_repo_mock.get_by_user_id.return_value = None
    student_repo_mock.create.return_value = {"id": uuid.uuid4(), "user_id": user_id}
    
    result = await student_service.create(student_data)
    assert result is not None

@pytest.mark.asyncio
async def test_duplicate_student_prevented(student_service, student_repo_mock):
    user_id = uuid.uuid4()
    student_data = {"user_id": user_id}
    student_repo_mock.get_by_user_id.return_value = {"id": uuid.uuid4(), "user_id": user_id}
    
    with pytest.raises(BusinessRuleViolation, match="already exists"):
        await student_service.create(student_data)

@pytest.mark.asyncio
async def test_missing_related_entity(student_service, student_repo_mock):
    student_data = {"user_id": None}
    
    with pytest.raises(EntityNotFound, match="not found"):
        await student_service.create(student_data)
