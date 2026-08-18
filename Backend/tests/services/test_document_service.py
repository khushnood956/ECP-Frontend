from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.document import Document
from app.models.enums import UserRole
from app.services.document_service import DocumentService
from app.services.exceptions import BusinessRuleViolation, PermissionDenied


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
async def test_service_upload_validation_oversized():
    repo = MagicMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()
    
    service = DocumentService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    # 11MB file (limit is 10MB)
    oversized_content = b"a" * (11 * 1024 * 1024)
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile

    with pytest.raises(BusinessRuleViolation) as exc:
        await service.create_document(
            filename="Passport.pdf",
            content_type="application/pdf",
            doc_type="ID",
            file_content=oversized_content,
            user=user
        )
    assert "exceeds the maximum limit" in str(exc.value)

@pytest.mark.asyncio
async def test_service_upload_validation_invalid_type():
    repo = MagicMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()
    
    service = DocumentService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile

    # Invalid MIME type (.exe)
    with pytest.raises(BusinessRuleViolation) as exc:
        await service.create_document(
            filename="malware.exe",
            content_type="application/octet-stream",
            doc_type="Other",
            file_content=b"test",
            user=user
        )
    assert "extension" in str(exc.value)

@pytest.mark.asyncio
async def test_service_upload_s3_failure():
    repo = MagicMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()
    
    service = DocumentService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile

    # Mock S3 upload failure
    service.storage.upload = AsyncMock(return_value=False)

    with pytest.raises(BusinessRuleViolation) as exc:
        await service.create_document(
            filename="Passport.pdf",
            content_type="application/pdf",
            doc_type="ID",
            file_content=b"test bytes",
            user=user
        )
    assert "Failed to upload" in str(exc.value)

@pytest.mark.asyncio
async def test_service_upload_db_failure_s3_cleanup():
    repo = AsyncMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()
    
    # Mock transaction context manager
    tx_context = AsyncMock()
    tx_manager.transaction.return_value = tx_context
    
    service = DocumentService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile

    # Mock successful S3 upload
    service.storage.upload = AsyncMock(return_value=True)
    # Mock S3 delete
    service.storage.delete = AsyncMock(return_value=True)
    # Mock DB insertion error
    repo.create.side_effect = Exception("DB Connection Lost")

    with pytest.raises(Exception) as exc:
        await service.create_document(
            filename="Passport.pdf",
            content_type="application/pdf",
            doc_type="ID",
            file_content=b"test bytes",
            user=user
        )
    assert "DB Connection Lost" in str(exc.value)
    # Ensure S3 object key is deleted
    service.storage.delete.assert_called_once()

@pytest.mark.asyncio
async def test_service_delete_document_success():
    repo = AsyncMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()
    
    # Mock transaction context manager
    tx_context = AsyncMock()
    tx_manager.transaction.return_value = tx_context
    
    service = DocumentService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    doc_id = uuid4()
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile

    mock_doc = Document(
        id=doc_id,
        student_profile_id=str(student_profile.id),
        filename="Passport.pdf",
        s3_key="students/123/documents/Passport.pdf"
    )
    repo.get_by_id.return_value = mock_doc
    service.storage.delete = AsyncMock(return_value=True)
    repo.delete.return_value = True

    result = await service.delete(doc_id, user)
    assert result is True
    service.storage.delete.assert_called_once_with(mock_doc.s3_key)

@pytest.mark.asyncio
async def test_service_delete_document_permission_denied():
    repo = AsyncMock()
    student_repo = AsyncMock()
    tx_manager = MagicMock()
    
    service = DocumentService(repository=repo, student_repository=student_repo, transaction_manager=tx_manager)
    
    doc_id = uuid4()
    user = MockUser()
    student_profile = MockStudentProfile(user.id)
    student_repo.get_by_user_id.return_value = student_profile

    # Document belongs to someone else
    mock_doc = Document(
        id=doc_id,
        student_profile_id=str(uuid4()),
        filename="Passport.pdf",
        s3_key="students/123/documents/Passport.pdf"
    )
    repo.get_by_id.return_value = mock_doc

    with pytest.raises(PermissionDenied) as exc:
        await service.delete(doc_id, user)
    assert "permission" in str(exc.value)
