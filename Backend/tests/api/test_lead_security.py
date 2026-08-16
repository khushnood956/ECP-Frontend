"""
Lead Security & Authorization Regression Tests.
Tests LEAD-01 through LEAD-20+ covering:
- Authorization (role-based access)
- Legacy endpoint security hardening
- Ownership enforcement (IDOR prevention)
- Lifecycle validation
- Schema validation
- Mass assignment prevention
"""
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import LeadStatus, UserRole
from app.models.user import User
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityNotFound,
    PermissionDenied,
)
from main import app

# --- Fixtures ---

TEST_STUDENT_USER_ID = str(uuid4())
TEST_AGENCY_USER_ID = str(uuid4())
TEST_ADMIN_USER_ID = str(uuid4())

def _student_user():
    return User(id=TEST_STUDENT_USER_ID, email="student@test.com", is_active=True, role=UserRole.STUDENT)

def _agency_user():
    return User(id=TEST_AGENCY_USER_ID, email="agency@test.com", is_active=True, role=UserRole.AGENCY)

def _admin_user():
    return User(id=TEST_ADMIN_USER_ID, email="admin@test.com", is_active=True, role=UserRole.ADMIN)


class MockLead:
    def __init__(self, lead_id=None, student_id=None, scholarship_id=None, agency_id=None, status=LeadStatus.NEW):
        self.id = lead_id or uuid4()
        self.student_id = student_id or uuid4()
        self.scholarship_id = scholarship_id or uuid4()
        self.agency_id = agency_id or uuid4()
        self.status = status
        self.notes = '{"motivation_letter": "Test", "documents": null, "notes": null}'
        self.status_updated_at = None
        self.follow_up_date = None
        self.created_at = "2026-08-07T15:00:00Z"
        self.updated_at = "2026-08-07T15:00:00Z"


@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_active_user] = _student_user
    yield
    app.dependency_overrides.clear()


# ========================
# LEAD-01: Student can create a lead
# ========================
@pytest.mark.asyncio
async def test_lead_01_student_can_create():
    with patch('app.services.lead_service.LeadService.create', new_callable=AsyncMock) as mock:
        mock.return_value = MockLead()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/leads", json={"scholarship_id": str(uuid4())})
        assert response.status_code == 201


# ========================
# LEAD-02: Agency cannot create a lead
# ========================
@pytest.mark.asyncio
async def test_lead_02_agency_cannot_create():
    app.dependency_overrides[get_current_active_user] = _agency_user
    with patch('app.services.lead_service.LeadService.create', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("Only student users can apply for scholarships.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/leads", json={"scholarship_id": str(uuid4())})
        assert response.status_code == 403


# ========================
# LEAD-03: Admin cannot create a lead
# ========================
@pytest.mark.asyncio
async def test_lead_03_admin_cannot_create():
    app.dependency_overrides[get_current_active_user] = _admin_user
    with patch('app.services.lead_service.LeadService.create', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("Only student users can apply for scholarships.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/leads", json={"scholarship_id": str(uuid4())})
        assert response.status_code == 403


# ========================
# LEAD-04: Student cannot view another student's lead (IDOR)
# ========================
@pytest.mark.asyncio
async def test_lead_04_student_idor_blocked():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.get_by_id', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("You do not have permission to view this lead.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 403


# ========================
# LEAD-05: Agency cannot view lead from another agency's scholarship
# ========================
@pytest.mark.asyncio
async def test_lead_05_agency_cross_access_blocked():
    app.dependency_overrides[get_current_active_user] = _agency_user
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.get_by_id', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("You do not have permission to view this lead.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 403


# ========================
# LEAD-06: Admin can view any lead
# ========================
@pytest.mark.asyncio
async def test_lead_06_admin_can_view_any_lead():
    app.dependency_overrides[get_current_active_user] = _admin_user
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.get_by_id', new_callable=AsyncMock) as mock:
        mock.return_value = MockLead(lead_id=lead_id)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == str(lead_id)


# ========================
# LEAD-07: Student cannot update another student's lead
# ========================
@pytest.mark.asyncio
async def test_lead_07_student_cannot_update_others():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("You do not have permission to modify this lead.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={"motivation_letter": "hacked"})
        assert response.status_code == 403


# ========================
# LEAD-08: Student cannot delete another student's lead
# ========================
@pytest.mark.asyncio
async def test_lead_08_student_cannot_delete_others():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.delete', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("You do not have permission to withdraw this lead.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 403


# ========================
# LEAD-09: Agency cannot delete leads
# ========================
@pytest.mark.asyncio
async def test_lead_09_agency_cannot_delete():
    app.dependency_overrides[get_current_active_user] = _agency_user
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.delete', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("Agencies are not allowed to delete applications.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 403


# ========================
# LEAD-10: Legacy assign-agency requires Admin
# ========================
@pytest.mark.asyncio
async def test_lead_10_assign_agency_student_forbidden():
    """Student cannot use the assign-agency endpoint."""
    lead_id = uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/v1/leads/{lead_id}/assign-agency?agency_id={uuid4()}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_lead_10b_assign_agency_agency_forbidden():
    """Agency user cannot use the assign-agency endpoint."""
    app.dependency_overrides[get_current_active_user] = _agency_user
    lead_id = uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/v1/leads/{lead_id}/assign-agency?agency_id={uuid4()}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_lead_10c_assign_agency_admin_allowed():
    """Admin can use the assign-agency endpoint."""
    app.dependency_overrides[get_current_active_user] = _admin_user
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.assign_agency', new_callable=AsyncMock) as mock:
        mock.return_value = MockLead(lead_id=lead_id)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/api/v1/leads/{lead_id}/assign-agency?agency_id={uuid4()}")
        assert response.status_code == 200


# ========================
# LEAD-11: Legacy status endpoint requires Admin
# ========================
@pytest.mark.asyncio
async def test_lead_11_status_endpoint_student_forbidden():
    """Student cannot use the legacy status endpoint."""
    lead_id = uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/v1/leads/{lead_id}/status", json={"status": "under_review"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_lead_11b_status_endpoint_agency_forbidden():
    """Agency user cannot use the legacy status endpoint."""
    app.dependency_overrides[get_current_active_user] = _agency_user
    lead_id = uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/v1/leads/{lead_id}/status", json={"status": "under_review"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_lead_11c_status_endpoint_admin_allowed():
    """Admin can use the legacy status endpoint."""
    app.dependency_overrides[get_current_active_user] = _admin_user
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update_status', new_callable=AsyncMock) as mock:
        mock.return_value = MockLead(lead_id=lead_id, status=LeadStatus.CONTACTED)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/api/v1/leads/{lead_id}/status", json={"status": "under_review"})
        assert response.status_code == 200


# ========================
# LEAD-12: Student/{student_id} endpoint ownership enforcement
# ========================
@pytest.mark.asyncio
async def test_lead_12_student_endpoint_idor_blocked():
    """Student cannot query leads for another student's profile."""
    other_student_id = uuid4()
    with patch('app.services.lead_service.LeadService.leads_by_student', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("You do not have permission to view these leads.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/leads/student/{other_student_id}")
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_lead_12b_agency_student_endpoint_blocked():
    """Agency user cannot use the student/{student_id} endpoint."""
    app.dependency_overrides[get_current_active_user] = _agency_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/leads/student/{uuid4()}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_lead_12c_admin_student_endpoint_allowed():
    """Admin can use the student/{student_id} endpoint."""
    app.dependency_overrides[get_current_active_user] = _admin_user
    with patch('app.services.lead_service.LeadService.leads_by_student', new_callable=AsyncMock) as mock:
        mock.return_value = [MockLead()]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/leads/student/{uuid4()}")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1


# ========================
# LEAD-13: Invalid lifecycle transition rejected
# ========================
@pytest.mark.asyncio
async def test_lead_13_invalid_lifecycle_transition():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock:
        mock.side_effect = BusinessRuleViolation("Invalid status transition from 'submitted' to 'accepted'.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={"status": "accepted"})
        assert response.status_code == 400
        assert response.json()["error_code"] == "BUSINESS_RULE_VIOLATION"


# ========================
# LEAD-14: Student cannot change lead status
# ========================
@pytest.mark.asyncio
async def test_lead_14_student_status_change_forbidden():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("Students are not allowed to update the status field.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={"status": "under_review"})
        assert response.status_code == 403


# ========================
# LEAD-15: Student cannot modify after review
# ========================
@pytest.mark.asyncio
async def test_lead_15_cannot_modify_after_review():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock:
        mock.side_effect = BusinessRuleViolation("Cannot update application after it is reviewed.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={"motivation_letter": "updated"})
        assert response.status_code == 400


# ========================
# LEAD-16: Cannot withdraw after review
# ========================
@pytest.mark.asyncio
async def test_lead_16_cannot_withdraw_after_review():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.delete', new_callable=AsyncMock) as mock:
        mock.side_effect = BusinessRuleViolation("Cannot withdraw application after it has been reviewed.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 400


# ========================
# LEAD-17: Lead not found returns 404
# ========================
@pytest.mark.asyncio
async def test_lead_17_not_found():
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.get_by_id', new_callable=AsyncMock) as mock:
        mock.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 404


# ========================
# LEAD-18: Invalid scholarship_id on create
# ========================
@pytest.mark.asyncio
async def test_lead_18_invalid_scholarship():
    with patch('app.services.lead_service.LeadService.create', new_callable=AsyncMock) as mock:
        mock.side_effect = EntityNotFound("Scholarship with id not found.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/leads", json={"scholarship_id": str(uuid4())})
        assert response.status_code == 404


# ========================
# LEAD-19: Duplicate lead rejected
# ========================
@pytest.mark.asyncio
async def test_lead_19_duplicate_rejected():
    from app.services.exceptions import EntityAlreadyExists
    with patch('app.services.lead_service.LeadService.create', new_callable=AsyncMock) as mock:
        mock.side_effect = EntityAlreadyExists("You have already applied for this scholarship.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/leads", json={"scholarship_id": str(uuid4())})
        assert response.status_code == 409


# ========================
# LEAD-20: Missing JWT returns 401
# ========================
@pytest.mark.asyncio
async def test_lead_20_missing_jwt():
    app.dependency_overrides.clear()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/leads")
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = _student_user


# ========================
# LEAD-21: Invalid UUID returns 422
# ========================
@pytest.mark.asyncio
async def test_lead_21_invalid_uuid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/leads/not-a-uuid")
    assert response.status_code == 422


# ========================
# LEAD-22: Agency mass-assignment of student fields blocked
# ========================
@pytest.mark.asyncio
async def test_lead_22_agency_mass_assignment_blocked():
    app.dependency_overrides[get_current_active_user] = _agency_user
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock:
        mock.side_effect = PermissionDenied("Agencies are not allowed to update student-owned fields.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={
                "motivation_letter": "injected",
                "documents": "injected",
                "notes": "injected"
            })
        assert response.status_code == 403


# ========================
# LEAD-23: Admin can delete any lead
# ========================
@pytest.mark.asyncio
async def test_lead_23_admin_can_delete():
    app.dependency_overrides[get_current_active_user] = _admin_user
    lead_id = uuid4()
    with patch('app.services.lead_service.LeadService.delete', new_callable=AsyncMock) as mock:
        mock.return_value = True
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 200


# ========================
# LEAD-24: LeadResponse includes follow_up_date
# ========================
@pytest.mark.asyncio
async def test_lead_24_response_includes_follow_up_date():
    lead_id = uuid4()
    mock_lead = MockLead(lead_id=lead_id)
    mock_lead.follow_up_date = "2026-09-01T12:00:00Z"
    with patch('app.services.lead_service.LeadService.get_by_id', new_callable=AsyncMock) as mock:
        mock.return_value = mock_lead
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 200
        assert response.json()["data"]["follow_up_date"] is not None


# ========================
# LEAD-25: Admin can update lead status + notes
# ========================
@pytest.mark.asyncio
async def test_lead_25_admin_full_update():
    app.dependency_overrides[get_current_active_user] = _admin_user
    lead_id = uuid4()
    mock_lead = MockLead(lead_id=lead_id, status=LeadStatus.CONTACTED)
    mock_lead.notes = '{"motivation_letter": "admin edited", "documents": null, "notes": "admin note"}'
    with patch('app.services.lead_service.LeadService.update', new_callable=AsyncMock) as mock:
        mock.return_value = mock_lead
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/leads/{lead_id}", json={
                "status": "under_review",
                "motivation_letter": "admin edited",
                "notes": "admin note"
            })
        assert response.status_code == 200
