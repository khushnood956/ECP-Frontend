from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.bookmark import Bookmark
from app.models.enums import UserRole
from app.services.bookmark_service import BookmarkService
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityNotFound,
    PermissionDenied,
)


class MockUser:
    def __init__(self, role=UserRole.STUDENT):
        self.id = uuid4()
        self.email = "student@test.com"
        self.role = role

class MockStudentProfile:
    def __init__(self, user_id):
        self.id = uuid4()
        self.user_id = user_id

@pytest.mark.asyncio
async def test_service_create_bookmark_success():
    repo = AsyncMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()
    tx_context = AsyncMock()
    tx_manager.transaction.return_value = tx_context

    service = BookmarkService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile
    repo.get_by_student_and_resource.return_value = None

    bookmark_id = uuid4()
    repo.create.return_value = Bookmark(id=bookmark_id, student_profile_id=student_profile.id, bookmark_type="scholarship")

    result = await service.create_bookmark(
        bookmark_type="scholarship",
        scholarship_id=uuid4(),
        university_id=None,
        current_user=user
    )
    assert result is not None
    repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_service_create_bookmark_duplicate_fails():
    repo = AsyncMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()

    service = BookmarkService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile
    repo.get_by_student_and_resource.return_value = Bookmark()

    with pytest.raises(BusinessRuleViolation) as exc:
        await service.create_bookmark(
            bookmark_type="scholarship",
            scholarship_id=uuid4(),
            university_id=None,
            current_user=user
        )
    assert "already exists" in str(exc.value)

@pytest.mark.asyncio
async def test_service_delete_bookmark_permission_denied():
    repo = AsyncMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()

    service = BookmarkService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile

    # Bookmark belongs to another student
    other_student_id = uuid4()
    mock_bookmark = Bookmark(id=uuid4(), student_profile_id=other_student_id, bookmark_type="scholarship")
    repo.get_by_id.return_value = mock_bookmark

    with pytest.raises(PermissionDenied) as exc:
        await service.delete_bookmark(mock_bookmark.id, user)
    assert "permission" in str(exc.value)

@pytest.mark.asyncio
async def test_service_delete_bookmark_not_found():
    repo = AsyncMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()

    service = BookmarkService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile

    repo.get_by_id.return_value = None

    with pytest.raises(EntityNotFound) as exc:
        await service.delete_bookmark(uuid4(), user)
    assert "not found" in str(exc.value)
