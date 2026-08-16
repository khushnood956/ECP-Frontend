from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import AgencyVerificationStatus, UserRole
from app.models.user import User
from app.services.exceptions import (
    EntityAlreadyExists,
    PermissionDenied,
)
from main import app

TEST_AGENCY_USER_ID = str(uuid4())
def override_get_current_active_user():
    return User(id=TEST_AGENCY_USER_ID, email="agency@agency.com", is_active=True, role=UserRole.AGENCY)

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    yield
    app.dependency_overrides.clear()

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
        return User(id=str(uuid4()), email="student@student.com", is_active=True, role=UserRole.STUDENT)
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
        return User(id=str(uuid4()), email="admin@admin.com", is_active=True, role=UserRole.ADMIN)
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
        mock_get.return_value = MockAgency(agency_id=agency_id, user_id=TEST_AGENCY_USER_ID)
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
async def test_get_agencies_non_admin_filtering():
    def get_student_user():
        return User(id=str(uuid4()), email="student@student.com", is_active=True, role=UserRole.STUDENT)
    app.dependency_overrides[get_current_active_user] = get_student_user

    with patch('app.services.base.BaseService.list', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Pass a suspended status. The router should override it to VERIFIED
            response = await client.get("/api/v1/agencies?verification_status=rejected")
        
        # Verify it called list with verification_status = VERIFIED
        kwargs = mock_list.call_args.kwargs
        assert kwargs.get("verification_status") == AgencyVerificationStatus.VERIFIED
        assert response.status_code == 200

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

@pytest.mark.asyncio
async def test_get_agencies_admin_filtering():
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@admin.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    with patch('app.services.base.BaseService.list', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/agencies?verification_status=rejected")
        
        kwargs = mock_list.call_args.kwargs
        assert kwargs.get("verification_status") == AgencyVerificationStatus.REJECTED
        assert response.status_code == 200

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


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
    with patch('app.services.agency_service.AgencyService.delete', new_callable=AsyncMock) as mock_delete, \
         patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockAgency(agency_id=agency_id, user_id=TEST_AGENCY_USER_ID)
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
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get, \
         patch('app.repositories.agency_repository.AgencyRepository.get_by_user_id', new_callable=AsyncMock) as mock_get_by_user:
        mock_get.return_value = None
        mock_get_by_user.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/agencies/{agency_id}")
        assert response.status_code == 404
        assert response.json()["error_code"] == "NOT_FOUND"

@pytest.mark.asyncio
async def test_non_admin_cannot_view_pending_agency():
    def get_student_user():
        return User(id=str(uuid4()), email="student@student.com", is_active=True, role=UserRole.STUDENT)
    app.dependency_overrides[get_current_active_user] = get_student_user

    agency_id = uuid4()
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_agency = MockAgency(agency_id=agency_id)
        mock_agency.verification_status = AgencyVerificationStatus.PENDING
        mock_get.return_value = mock_agency
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/agencies/{agency_id}")
        assert response.status_code == 403

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

@pytest.mark.asyncio
async def test_admin_can_view_pending_agency():
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@admin.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    agency_id = uuid4()
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_agency = MockAgency(agency_id=agency_id)
        mock_agency.verification_status = AgencyVerificationStatus.PENDING
        mock_get.return_value = mock_agency
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/agencies/{agency_id}")
        assert response.status_code == 200

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_non_admin_cannot_view_pending_by_registration():
    def get_student_user():
        return User(id=str(uuid4()), email="student@student.com", is_active=True, role=UserRole.STUDENT)
    app.dependency_overrides[get_current_active_user] = get_student_user

    with patch('app.services.agency_service.AgencyService.get_by_registration_number', new_callable=AsyncMock) as mock_get:
        mock_agency = MockAgency()
        mock_agency.verification_status = AgencyVerificationStatus.PENDING
        mock_get.side_effect = PermissionDenied("You do not have permission to view this agency profile.")
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/agencies/registration/REG-1001")
        assert response.status_code == 403

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

@pytest.mark.asyncio
async def test_non_admin_cannot_view_rejected_by_registration():
    def get_student_user():
        return User(id=str(uuid4()), email="student@student.com", is_active=True, role=UserRole.STUDENT)
    app.dependency_overrides[get_current_active_user] = get_student_user

    with patch('app.services.agency_service.AgencyService.get_by_registration_number', new_callable=AsyncMock) as mock_get:
        mock_agency = MockAgency()
        mock_agency.verification_status = AgencyVerificationStatus.REJECTED
        mock_get.side_effect = PermissionDenied("You do not have permission to view this agency profile.")
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/agencies/registration/REG-1001")
        assert response.status_code == 403

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

@pytest.mark.asyncio
async def test_non_admin_can_view_verified_by_registration():
    def get_student_user():
        return User(id=str(uuid4()), email="student@student.com", is_active=True, role=UserRole.STUDENT)
    app.dependency_overrides[get_current_active_user] = get_student_user

    with patch('app.services.agency_service.AgencyService.get_by_registration_number', new_callable=AsyncMock) as mock_get:
        mock_agency = MockAgency()
        mock_agency.verification_status = AgencyVerificationStatus.VERIFIED
        mock_get.return_value = mock_agency
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/agencies/registration/REG-1001")
        assert response.status_code == 200
        assert response.json()["data"]["verification_status"] == "verified"

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

@pytest.mark.asyncio
async def test_admin_can_view_pending_by_registration():
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@admin.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    with patch('app.services.agency_service.AgencyService.get_by_registration_number', new_callable=AsyncMock) as mock_get:
        mock_agency = MockAgency()
        mock_agency.verification_status = AgencyVerificationStatus.PENDING
        mock_get.return_value = mock_agency
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/agencies/registration/REG-1001")
        assert response.status_code == 200

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

@pytest.mark.asyncio
async def test_agency_owner_can_view_own_pending_by_registration():
    agency_owner_user_id = str(uuid4())
    def get_owner_user():
        return User(id=agency_owner_user_id, email="owner@agency.com", is_active=True, role=UserRole.AGENCY)
    app.dependency_overrides[get_current_active_user] = get_owner_user

    with patch('app.services.agency_service.AgencyService.get_by_registration_number', new_callable=AsyncMock) as mock_get:
        mock_agency = MockAgency(user_id=agency_owner_user_id)
        mock_agency.verification_status = AgencyVerificationStatus.PENDING
        mock_get.return_value = mock_agency
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/agencies/registration/REG-1001")
        assert response.status_code == 200

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_get_my_agency_success():
    with patch('app.services.agency_service.AgencyService.get_by_user_id', new_callable=AsyncMock) as mock_get:
        mock_agency = MockAgency(user_id=TEST_AGENCY_USER_ID)
        mock_agency.verification_status = AgencyVerificationStatus.PENDING
        mock_get.return_value = mock_agency
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/agencies/me")
        
        assert response.status_code == 200
        assert response.json()["data"]["user_id"] == TEST_AGENCY_USER_ID


@pytest.mark.asyncio
async def test_get_my_agency_not_found():
    with patch('app.services.agency_service.AgencyService.get_by_user_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/agencies/me")
        
        assert response.status_code == 404


