from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import LeadStatus, UserRole
from app.models.user import User
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityAlreadyExists,
    PermissionDenied,
)
from main import app

TEST_LEAD_USER_ID = str(uuid4())
def override_get_current_active_user():
    return User(id=TEST_LEAD_USER_ID, email="student@lead.com", is_active=True, role=UserRole.STUDENT)

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    yield
    app.dependency_overrides.clear()

class MockLead:
    def __init__(self, lead_id=None, student_id=None, scholarship_id=None, agency_id=None):
        self.id = lead_id or uuid4()
        self.student_id = student_id or uuid4()
        self.scholarship_id = scholarship_id or uuid4()
        self.agency_id = agency_id or uuid4()
        self.status = LeadStatus.NEW
        self.notes = '{"motivation_letter": "I want this scholarship because...", "documents": "cv.pdf", "notes": "Ready to travel."}'
        self.status_updated_at = None
        self.created_at = "2026-08-07T15:00:00Z"
        self.updated_at = "2026-08-07T15:00:00Z"


@pytest.mark.asyncio
async def test_create_lead():
    with patch('app.services.lead_service.LeadService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockLead()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/leads", json={
                "scholarship_id": str(uuid4()),
                "motivation_letter": "I want this scholarship because...",
                "notes": "Ready to travel."
            })
        assert response.status_code == 201
        assert response.json()["data"]["status"] == "submitted"
        assert response.json()["data"]["motivation_letter"] == "I want this scholarship because..."


@pytest.mark.asyncio
async def test_duplicate_prevention():
    with patch('app.services.lead_service.LeadService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = EntityAlreadyExists("You have already applied for this scholarship.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/leads", json={
                "scholarship_id": str(uuid4())
            })
        assert response.status_code == 409
        assert response.json()["error_code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_past_deadline():
    with patch('app.services.lead_service.LeadService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Scholarship deadline has passed.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/leads", json={
                "scholarship_id": str(uuid4())
            })
        assert response.status_code == 400
        assert response.json()["error_code"] == "BUSINESS_RULE_VIOLATION"


@pytest.mark.asyncio
async def test_scholarship_inactive():
    with patch('app.services.lead_service.LeadService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Scholarship is inactive.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/leads", json={
                "scholarship_id": str(uuid4())
            })
        assert response.status_code == 400
        assert response.json()["error_code"] == "BUSINESS_RULE_VIOLATION"


@pytest.mark.asyncio
async def test_get_lead_by_id():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockLead(lead_id=lead_id)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == str(lead_id)


@pytest.mark.asyncio
async def test_get_lead_list():
    class MockPaginatedResult:
        def __init__(self):
            self.items = [MockLead(), MockLead()]
            self.total = 2
            self.page = 1
            self.page_size = 10
            self.total_pages = 1

    with patch('app.services.lead_service.LeadService.list_leads', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockPaginatedResult()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/leads")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 2


@pytest.mark.asyncio
async def test_student_update_application():
    lead_id = uuid4()
    mock_lead = MockLead(lead_id=lead_id)
    mock_lead.notes = '{"motivation_letter": "Updated letter.", "documents": "cv.pdf", "notes": "Ready to travel."}'

    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_lead
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={
                "motivation_letter": "Updated letter."
            })
        assert response.status_code == 200
        assert response.json()["data"]["motivation_letter"] == "Updated letter."


@pytest.mark.asyncio
async def test_student_patch_status_forbidden():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock_update:
        mock_update.side_effect = PermissionDenied("Students are not allowed to update the status field.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={
                "status": "under_review"
            })
        assert response.status_code == 403
        assert response.json()["error_code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_agency_status_update():
    def override_agency_user():
        return User(id=str(uuid4()), email="agency@lead.com", is_active=True, role="agency")
    app.dependency_overrides[get_current_active_user] = override_agency_user

    lead_id = uuid4()
    mock_lead = MockLead(lead_id=lead_id)
    mock_lead.status = LeadStatus.CONTACTED

    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_lead
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={
                "status": "under_review"
            })
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "under_review"

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_agency_patch_student_owned_fields_forbidden():
    def override_agency_user():
        return User(id=str(uuid4()), email="agency@lead.com", is_active=True, role="agency")
    app.dependency_overrides[get_current_active_user] = override_agency_user

    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock_update:
        mock_update.side_effect = PermissionDenied("Agencies are not allowed to update student-owned fields.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={
                "motivation_letter": "Hacked motivation"
            })
        assert response.status_code == 403
        assert response.json()["error_code"] == "FORBIDDEN"

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_agency_patch_another_agency_lead_forbidden():
    def override_agency_user():
        return User(id=str(uuid4()), email="agency@lead.com", is_active=True, role="agency")
    app.dependency_overrides[get_current_active_user] = override_agency_user

    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock_update:
        mock_update.side_effect = PermissionDenied("You do not have permission to view or modify this lead.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={
                "status": "under_review"
            })
        assert response.status_code == 403
        assert response.json()["error_code"] == "FORBIDDEN"

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_admin_patch_status_success():
    def override_admin_user():
        return User(id=str(uuid4()), email="admin@lead.com", is_active=True, role="admin")
    app.dependency_overrides[get_current_active_user] = override_admin_user

    lead_id = uuid4()
    mock_lead = MockLead(lead_id=lead_id)
    mock_lead.status = LeadStatus.CONTACTED

    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_lead
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={
                "status": "under_review"
            })
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "under_review"

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_invalid_status_transition():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock_update:
        mock_update.side_effect = BusinessRuleViolation("Invalid status transition.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={
                "status": "accepted"
            })
        assert response.status_code == 400
        assert response.json()["error_code"] == "BUSINESS_RULE_VIOLATION"


@pytest.mark.asyncio
async def test_student_withdraw():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Lead deleted successfully"


@pytest.mark.asyncio
async def test_withdraw_after_review():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.side_effect = BusinessRuleViolation("Cannot withdraw application after it has been reviewed.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 400
        assert response.json()["error_code"] == "BUSINESS_RULE_VIOLATION"


@pytest.mark.asyncio
async def test_lead_not_found():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 404
        assert response.json()["error_code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_missing_jwt():
    app.dependency_overrides.clear()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/leads")
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_invalid_jwt():
    app.dependency_overrides.clear()
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/leads", headers=headers)
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
