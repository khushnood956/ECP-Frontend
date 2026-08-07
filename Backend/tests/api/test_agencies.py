import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import patch, AsyncMock
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.enums import AgencyVerificationStatus
from app.services.exceptions import EntityNotFound, EntityAlreadyExists, PermissionDenied

def override_get_current_active_user():
    return User(id=str(uuid4()), email="agency@agency.com", is_active=True, role="agency")

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

class MockAgency:
    def __init__(self, agency_id=None, user_id=None, registration_number="REG-1001"):
        self.id = agency_id or uuid4()
        self.user_id = user_id or uuid4()
        self.agency_name = "ABC Education"
        self.description = "Educational consultancy"
        self.website = "https://abc.edu"
        self.logo_url = None
        self.registration_number = registration_number
        self.email = "info@abc.edu"
        self.phone = "+923001234567"
        self.country = "Pakistan"
        self.city = "Islamabad"
        self.address = "123 Main St"
        self.verification_status = AgencyVerificationStatus.PENDING
        self.verified_at = None
        self.created_at = "2026-01-01T00:00:00Z"
        self.updated_at = "2026-01-01T00:00:00Z"


@pytest.mark.asyncio
async def test_create_agency():
    with patch('app.services.agency_service.AgencyService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockAgency()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/agencies", json={
                "agency_name": "ABC Education",
                "registration_number": "REG-1001",
                "country": "Pakistan",
                "city": "Islamabad",
                "website": "https://abc.edu",
                "email": "info@abc.edu",
                "phone": "+923001234567"
            })
        assert response.status_code == 201
        assert response.json()["data"]["agency_name"] == "ABC Education"
        assert response.json()["data"]["registration_number"] == "REG-1001"


@pytest.mark.asyncio
async def test_student_cannot_create_agency():
    def get_student_user():
        return User(id=str(uuid4()), email="student@student.com", is_active=True, role="student")
    app.dependency_overrides[get_current_active_user] = get_student_user

    with patch('app.services.agency_service.AgencyService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Only agency users can create agency profiles.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/agencies", json={
                "agency_name": "ABC Education",
                "registration_number": "REG-1001"
            })
        assert response.status_code == 403
        assert response.json()["error_code"] == "FORBIDDEN"

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_admin_cannot_create_agency():
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@admin.com", is_active=True, role="admin")
    app.dependency_overrides[get_current_active_user] = get_admin_user

    with patch('app.services.agency_service.AgencyService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Only agency users can create agency profiles.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/agencies", json={
                "agency_name": "ABC Education",
                "registration_number": "REG-1001"
            })
        assert response.status_code == 403
        assert response.json()["error_code"] == "FORBIDDEN"

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_duplicate_agency_profile_for_user():
    with patch('app.services.agency_service.AgencyService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = EntityAlreadyExists("This user already has an agency profile.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/agencies", json={
                "agency_name": "ABC Education",
                "registration_number": "REG-1001"
            })
        assert response.status_code == 409
        assert response.json()["error_code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_get_agency():
    agency_id = uuid4()
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockAgency(agency_id=agency_id)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/agencies/{agency_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == str(agency_id)


@pytest.mark.asyncio
async def test_get_all_agencies():
    with patch('app.services.base.BaseService.list', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [MockAgency(), MockAgency()]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/agencies")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 2


@pytest.mark.asyncio
async def test_update_agency():
    agency_id = uuid4()
    mock_agency = MockAgency(agency_id=agency_id)
    mock_agency.agency_name = "XYZ Education"

    with patch('app.services.agency_service.AgencyService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_agency
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/agencies/{agency_id}", json={
                "agency_name": "XYZ Education"
            })
        assert response.status_code == 200
        assert response.json()["data"]["agency_name"] == "XYZ Education"


@pytest.mark.asyncio
async def test_delete_agency():
    agency_id = uuid4()
    with patch('app.services.base.BaseService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/agencies/{agency_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Agency deleted successfully"


@pytest.mark.asyncio
async def test_duplicate_registration_number():
    with patch('app.services.agency_service.AgencyService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = EntityAlreadyExists("Agency with registration number 'REG-1001' already exists.")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/agencies", json={
                "agency_name": "ABC Education",
                "registration_number": "REG-1001"
            })
        assert response.status_code == 409
        assert response.json()["error_code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_invalid_payload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Missing required agency_name
        response = await client.post("/api/v1/agencies", json={
            "description": "Invalid payload without required fields"
        })
    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_missing_jwt():
    app.dependency_overrides.clear()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/agencies")
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_invalid_jwt():
    app.dependency_overrides.clear()
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/agencies", headers=headers)
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_non_existing_agency():
    agency_id = uuid4()
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/agencies/{agency_id}")
        assert response.status_code == 404
        assert response.json()["error_code"] == "NOT_FOUND"
