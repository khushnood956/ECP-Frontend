from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import DegreeLevel, FundingType, UserRole
from app.models.user import User
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityAlreadyExists,
    PermissionDenied,
)
from main import app

TEST_SCHOLARSHIP_USER_ID = str(uuid4())
def override_get_current_active_user():
    return User(id=TEST_SCHOLARSHIP_USER_ID, email="agency@scholarship.com", is_active=True, role=UserRole.AGENCY)

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    yield
    app.dependency_overrides.clear()

class MockScholarship:
    def __init__(self, sch_id=None):
        self.id = sch_id or uuid4()
        self.title = "Full Tuition Scholarship"
        self.country = "USA"
        self.university = "Harvard University"
        self.degree_level = DegreeLevel.BACHELOR
        self.funding_type = FundingType.FULLY_FUNDED
        self.amount = 50000.00
        self.currency = "USD"
        self.deadline = "2026-12-31"
        self.eligibility = "CGPA > 3.8"
        self.description = "Fully funded undergraduate scholarship"
        self.application_link = "https://harvard.edu/apply"
        self.is_active = True
        self.created_at = "2026-01-01T00:00:00Z"
        self.updated_at = "2026-01-01T00:00:00Z"


@pytest.mark.asyncio
async def test_create_scholarship():
    with patch('app.services.scholarship_service.ScholarshipService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockScholarship()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/scholarships", json={
                "title": "Full Tuition Scholarship",
                "country": "USA",
                "university": "Harvard University",
                "degree_level": "bachelor",
                "funding_type": "fully_funded",
                "amount": 50000.00,
                "currency": "USD",
                "deadline": "2026-12-31"
            })
        assert response.status_code == 201
        assert response.json()["data"]["title"] == "Full Tuition Scholarship"
        assert response.json()["data"]["country"] == "USA"


@pytest.mark.asyncio
async def test_duplicate_validation():
    with patch('app.services.scholarship_service.ScholarshipService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = EntityAlreadyExists("Scholarship with title 'Full Tuition Scholarship' already exists.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/scholarships", json={
                "title": "Full Tuition Scholarship",
                "country": "USA",
                "degree_level": "bachelor",
                "funding_type": "fully_funded"
            })
        assert response.status_code == 409
        assert response.json()["error_code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_invalid_deadline():
    with patch('app.services.scholarship_service.ScholarshipService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Scholarship deadline cannot be in the past")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/scholarships", json={
                "title": "Past Scholarship",
                "country": "USA",
                "degree_level": "bachelor",
                "funding_type": "fully_funded",
                "deadline": "2020-01-01"
            })
        assert response.status_code == 400
        assert response.json()["error_code"] == "BUSINESS_RULE_VIOLATION"


@pytest.mark.asyncio
async def test_forbidden_role():
    def get_student_user():
        return User(id=str(uuid4()), email="student@scholarship.com", is_active=True, role="student")
    app.dependency_overrides[get_current_active_user] = get_student_user

    with patch('app.services.scholarship_service.ScholarshipService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Only agency users can create scholarships.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/scholarships", json={
                "title": "Forbidden Scholarship",
                "country": "USA",
                "degree_level": "bachelor",
                "funding_type": "fully_funded"
            })
        assert response.status_code == 403
        assert response.json()["error_code"] == "FORBIDDEN"

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_get_all_scholarships():
    class MockPaginatedResult:
        def __init__(self):
            self.items = [MockScholarship(), MockScholarship()]
            self.total = 2
            self.page = 1
            self.page_size = 10
            self.total_pages = 1

    with patch('app.repositories.base.BaseRepository.list_paginated', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockPaginatedResult()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/scholarships")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_scholarship_by_id():
    sch_id = uuid4()
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockScholarship(sch_id=sch_id)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/scholarships/{sch_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == str(sch_id)


@pytest.mark.asyncio
async def test_update_scholarship():
    sch_id = uuid4()
    mock_sch = MockScholarship(sch_id=sch_id)
    mock_sch.title = "Updated Scholarship Title"

    with patch('app.services.scholarship_service.ScholarshipService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_sch
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/scholarships/{sch_id}", json={
                "title": "Updated Scholarship Title"
            })
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated Scholarship Title"


@pytest.mark.asyncio
async def test_delete_scholarship():
    sch_id = uuid4()
    with patch('app.services.scholarship_service.ScholarshipService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/scholarships/{sch_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Scholarship deleted successfully"


@pytest.mark.asyncio
async def test_scholarship_not_found():
    sch_id = uuid4()
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/scholarships/{sch_id}")
        assert response.status_code == 404
        assert response.json()["error_code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_missing_jwt():
    app.dependency_overrides.clear()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/scholarships")
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_invalid_jwt():
    app.dependency_overrides.clear()
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/scholarships", headers=headers)
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
