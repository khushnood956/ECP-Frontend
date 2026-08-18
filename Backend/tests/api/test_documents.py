from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import UserRole
from app.models.user import User
from app.services.exceptions import PermissionDenied
from main import app

TEST_STUDENT_USER_ID = str(uuid4())

def _student_user():
    return User(id=TEST_STUDENT_USER_ID, email="student@test.com", is_active=True, role=UserRole.STUDENT)

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_active_user] = _student_user
    yield
    app.dependency_overrides.clear()

class MockDocument:
    def __init__(self, doc_id=None, student_profile_id=None):
        self.id = doc_id or uuid4()
        self.student_profile_id = student_profile_id or uuid4()
        self.filename = "Passport.pdf"
        self.doc_type = "ID"
        self.verified = False
        self.upload_date = "2026-08-17"
        self.file_size = 1000
        self.mime_type = "application/pdf"
        self.created_at = "2026-08-17T15:00:00Z"
        self.updated_at = "2026-08-17T15:00:00Z"

@pytest.mark.asyncio
async def test_create_document_success():
    with patch('app.services.document_service.DocumentService.create_document', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockDocument()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/student-profiles/documents",
                data={"doc_type": "ID"},
                files={"file": ("Passport.pdf", b"test content", "application/pdf")}
            )
        assert response.status_code == 201
        assert response.json()["data"]["filename"] == "Passport.pdf"
        assert response.json()["data"]["doc_type"] == "ID"

@pytest.mark.asyncio
async def test_get_documents_success():
    with patch('app.services.document_service.DocumentService.list_documents', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [MockDocument(), MockDocument()]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/student-profiles/documents")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 2

@pytest.mark.asyncio
async def test_get_download_url_success():
    with patch('app.services.document_service.DocumentService.get_download_url', new_callable=AsyncMock) as mock_download:
        mock_download.return_value = "https://mock-presigned-s3-url.com"
        doc_id = uuid4()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/student-profiles/documents/{doc_id}/download")
        assert response.status_code == 200
        assert response.json()["data"]["download_url"] == "https://mock-presigned-s3-url.com"

@pytest.mark.asyncio
async def test_delete_document_success():
    with patch('app.services.document_service.DocumentService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        doc_id = uuid4()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/student-profiles/documents/{doc_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Document deleted successfully"

@pytest.mark.asyncio
async def test_delete_document_permission_denied():
    with patch('app.services.document_service.DocumentService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.side_effect = PermissionDenied("You do not have permission to delete this document.")
        doc_id = uuid4()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/student-profiles/documents/{doc_id}")
        assert response.status_code == 403
        assert response.json()["error_code"] == "FORBIDDEN"
