from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.bookmark import BookmarkResponse
from app.services.exceptions import BusinessRuleViolation
from main import app

TEST_STUDENT_USER_ID = str(uuid4())

def _student_user():
    return User(id=TEST_STUDENT_USER_ID, email="student@test.com", is_active=True, role=UserRole.STUDENT)

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_active_user] = _student_user
    yield
    app.dependency_overrides.clear()

class MockBookmark:
    def __init__(self, bookmark_id=None, student_profile_id=None, bookmark_type="scholarship"):
        self.id = bookmark_id or uuid4()
        self.student_profile_id = student_profile_id or uuid4()
        self.bookmark_type = bookmark_type
        self.scholarship_id = uuid4() if bookmark_type == "scholarship" else None
        self.university_id = uuid4() if bookmark_type == "university" else None
        self.created_at = "2026-08-17T21:50:00Z"
        self.updated_at = "2026-08-17T21:50:00Z"
        self.scholarship = None
        self.university = None


class MockRequirement:
    def __init__(self):
        self.id = uuid4()
        self.scholarship_id = uuid4()
        self.field_key = "ielts_score"
        self.label = "IELTS Score"
        self.field_type = "text"
        self.is_required = True
        self.options = None
        self.display_order = 0

@pytest.mark.asyncio
async def test_create_scholarship_bookmark_success():
    with patch('app.services.bookmark_service.BookmarkService.create_bookmark', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockBookmark(bookmark_type="scholarship")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/bookmarks",
                json={"bookmark_type": "scholarship", "scholarship_id": str(uuid4())}
            )
        assert response.status_code == 201
        assert response.json()["data"]["bookmark_type"] == "scholarship"

@pytest.mark.asyncio
async def test_create_university_bookmark_success():
    with patch('app.services.bookmark_service.BookmarkService.create_bookmark', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockBookmark(bookmark_type="university")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/bookmarks",
                json={"bookmark_type": "university", "university_id": str(uuid4())}
            )
        assert response.status_code == 201
        assert response.json()["data"]["bookmark_type"] == "university"

@pytest.mark.asyncio
async def test_get_bookmarks_success():
    with patch('app.services.bookmark_service.BookmarkService.list_bookmarks', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [MockBookmark(bookmark_type="scholarship"), MockBookmark(bookmark_type="university")]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/bookmarks")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 2


@pytest.mark.asyncio
async def test_bookmark_response_serializes_nested_scholarship_requirements():
    bookmark = MockBookmark(bookmark_type="scholarship")
    scholarship = type(
        "MockScholarship",
        (),
        {
            "id": uuid4(),
            "title": "Global Excellence Scholarship",
            "country": "Canada",
            "university": "University of Toronto",
            "degree_level": "bachelor",
            "funding_type": "fully_funded",
            "amount": 10000,
            "currency": "USD",
            "deadline": None,
            "eligibility": None,
            "description": None,
            "application_link": None,
            "is_active": True,
            "agency_id": None,
            "created_at": "2026-08-17T21:50:00Z",
            "updated_at": "2026-08-17T21:50:00Z",
            "application_requirements": [MockRequirement()],
        },
    )()
    bookmark.scholarship = scholarship

    response = BookmarkResponse.model_validate(bookmark).model_dump()

    assert response["scholarship"]["application_requirements"][0]["field_key"] == "ielts_score"

@pytest.mark.asyncio
async def test_delete_bookmark_success():
    with patch('app.services.bookmark_service.BookmarkService.delete_bookmark', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        bookmark_id = uuid4()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/bookmarks/{bookmark_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Bookmark deleted successfully"

@pytest.mark.asyncio
async def test_create_bookmark_duplicate_rejected():
    with patch('app.services.bookmark_service.BookmarkService.create_bookmark', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Bookmark already exists.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/bookmarks",
                json={"bookmark_type": "scholarship", "scholarship_id": str(uuid4())}
            )
        assert response.status_code == 400
        assert response.json()["error_code"] == "BUSINESS_RULE_VIOLATION"
