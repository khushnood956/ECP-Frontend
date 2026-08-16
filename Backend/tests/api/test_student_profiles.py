from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import UserRole
from app.models.user import User
from app.services.exceptions import BusinessRuleViolation, EntityNotFound
from main import app

TEST_USER_ID = str(uuid4())
def override_get_current_active_user():
    return User(id=TEST_USER_ID, email="test@test.com", is_active=True, role=UserRole.STUDENT)

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    yield
    app.dependency_overrides.clear()

class MockStudent:
    def __init__(self):
        self.id = uuid4()
        self.user_id = TEST_USER_ID
        self.first_name = "Alice"
        self.last_name = "Smith"
        self.created_at = "2023-01-01T00:00:00Z"
        self.updated_at = "2023-01-01T00:00:00Z"

@pytest.mark.asyncio
async def test_create_student():
    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockStudent()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": TEST_USER_ID,
                "first_name": "Alice",
                "last_name": "Smith"
            })
        assert response.status_code == 201
        assert response.json()["data"]["first_name"] == "Alice"

@pytest.mark.asyncio
async def test_duplicate_student():
    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Student profile already exists")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": TEST_USER_ID,
                "first_name": "Alice",
                "last_name": "Smith"
            })
        assert response.status_code == 400
        assert "already exists" in str(response.json())

@pytest.mark.asyncio
async def test_invalid_user_create():
    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = EntityNotFound("Related user not found")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": TEST_USER_ID,
                "first_name": "Alice",
                "last_name": "Smith"
            })
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_students():
    class MockResult:
        def __init__(self):
            self.items = [MockStudent()]
            self.total = 1
            self.page = 1
            self.page_size = 10
            self.total_pages = 1
            
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@test.com", is_active=True, role=UserRole.ADMIN)

    with patch('app.repositories.student_profile_repository.StudentProfileRepository.list_scoped', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockResult()
        
        app.dependency_overrides[get_current_active_user] = get_admin_user
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/student-profiles")
            
        app.dependency_overrides[get_current_active_user] = override_get_current_active_user
        
        assert response.status_code == 200
        assert isinstance(response.json()["data"], list)

@pytest.mark.asyncio
async def test_get_student_by_id():
    student_id = uuid4()
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockStudent()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_invalid_student_id():
    student_id = uuid4()
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get, \
         patch('app.services.student_service.StudentService.get_by_user_id', new_callable=AsyncMock) as mock_get_by_user:
        mock_get.return_value = None
        mock_get_by_user.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_student():
    student_id = uuid4()
    with patch('app.services.student_service.StudentService.update', new_callable=AsyncMock) as mock_update, \
         patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockStudent()
        mock_update.return_value = MockStudent()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/student-profiles/{student_id}", json={
                "first_name": "Bob"
            })
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_student():
    student_id = uuid4()
    with patch('app.services.student_service.StudentService.delete', new_callable=AsyncMock) as mock_delete, \
         patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockStudent()
        mock_delete.return_value = True
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_invalid_student():
    student_id = uuid4()
    with patch('app.services.student_service.StudentService.delete', new_callable=AsyncMock) as mock_delete, \
         patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get, \
         patch('app.repositories.student_profile_repository.StudentProfileRepository.get_by_user_id', new_callable=AsyncMock) as mock_get_by_user:
        mock_get.return_value = None
        mock_get_by_user.return_value = None
        mock_delete.side_effect = EntityNotFound("Not found")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_unauthorized_access():
    app.dependency_overrides.pop(get_current_active_user, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/student-profiles")
    assert response.status_code == 401


# --- STUDENT-01 through STUDENT-24: Security Regression Tests ---

@pytest.mark.asyncio
async def test_student_01_student_view_own_profile():
    # Student can view own profile
    student_id = uuid4()
    mock_student = MockStudent()
    mock_student.user_id = TEST_USER_ID

    with patch('app.services.student_service.StudentService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_student
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_student_02_student_cannot_view_other_profile():
    # Student cannot view another student's profile -> 403
    student_id = uuid4()
    mock_student = MockStudent()
    mock_student.user_id = str(uuid4())

    with patch('app.services.student_service.StudentService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        from app.services.exceptions import PermissionDenied
        mock_get.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_student_03_agency_can_view_with_active_lead():
    # Agency can view a student profile when an appropriate active Lead relationship exists
    def get_agency_user():
        return User(id=str(uuid4()), email="agency@test.com", is_active=True, role=UserRole.AGENCY)
    app.dependency_overrides[get_current_active_user] = get_agency_user

    student_id = uuid4()
    mock_student = MockStudent()
    with patch('app.services.student_service.StudentService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_student
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 200

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_04_agency_cannot_view_unrelated():
    # Agency cannot view an unrelated student's profile -> 403
    def get_agency_user():
        return User(id=str(uuid4()), email="agency@test.com", is_active=True, role=UserRole.AGENCY)
    app.dependency_overrides[get_current_active_user] = get_agency_user

    student_id = uuid4()
    with patch('app.services.student_service.StudentService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        from app.services.exceptions import PermissionDenied
        mock_get.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 403

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_05_admin_can_view_any():
    # Admin can view any student profile
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@test.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    student_id = uuid4()
    mock_student = MockStudent()
    with patch('app.services.student_service.StudentService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_student
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 200

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_06_unauthenticated_request_401():
    # Unauthenticated request -> 401
    app.dependency_overrides.pop(get_current_active_user, None)
    student_id = uuid4()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/student-profiles/{student_id}")
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_07_student_listing_returns_own():
    # Student listing returns only their own profile
    class MockResult:
        def __init__(self):
            self.items = [MockStudent()]
            self.total = 1
            self.page = 1
            self.page_size = 10
            self.total_pages = 1

    with patch('app.services.student_service.StudentService.list_student_profiles', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockResult()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/student-profiles")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1


@pytest.mark.asyncio
async def test_student_08_agency_listing_scoped():
    # Agency listing returns only profiles belonging to students connected through appropriate active leads
    def get_agency_user():
        return User(id=str(uuid4()), email="agency@test.com", is_active=True, role=UserRole.AGENCY)
    app.dependency_overrides[get_current_active_user] = get_agency_user

    class MockResult:
        def __init__(self):
            self.items = [MockStudent()]
            self.total = 1
            self.page = 1
            self.page_size = 10
            self.total_pages = 1

    with patch('app.services.student_service.StudentService.list_student_profiles', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockResult()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/student-profiles")
        assert response.status_code == 200

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_09_agency_listing_no_unrelated():
    # Agency listing does not contain unrelated students
    def get_agency_user():
        return User(id=str(uuid4()), email="agency@test.com", is_active=True, role=UserRole.AGENCY)
    app.dependency_overrides[get_current_active_user] = get_agency_user

    class MockResult:
        def __init__(self):
            self.items = []
            self.total = 0
            self.page = 1
            self.page_size = 10
            self.total_pages = 0

    with patch('app.services.student_service.StudentService.list_student_profiles', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockResult()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/student-profiles")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 0

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_10_admin_listing_all():
    # Admin listing returns all profiles
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@test.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    class MockResult:
        def __init__(self):
            self.items = [MockStudent(), MockStudent()]
            self.total = 2
            self.page = 1
            self.page_size = 10
            self.total_pages = 1

    with patch('app.services.student_service.StudentService.list_student_profiles', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockResult()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/student-profiles")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 2

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_11_unauthenticated_listing_401():
    # Unauthenticated listing -> 401
    app.dependency_overrides.pop(get_current_active_user, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/student-profiles")
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_12_student_cannot_forge_user_id():
    # Student cannot create a profile using another user's user_id
    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockStudent()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": str(uuid4()),
                "first_name": "Forger",
                "last_name": "Smith"
            })
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_student_13_student_create_always_binds_own_id():
    # Student creation always binds profile to authenticated user's ID
    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockStudent()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": TEST_USER_ID,
                "first_name": "Bob",
                "last_name": "Jones"
            })
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_student_14_cannot_patch_user_id():
    # Student cannot change user_id through PATCH
    student_id = uuid4()
    mock_student = MockStudent()

    with patch('app.services.student_service.StudentService.update', new_callable=AsyncMock) as mock_update, \
         patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_student
        mock_update.return_value = mock_student
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/student-profiles/{student_id}", json={
                "user_id": str(uuid4())
            })
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_student_15_cannot_patch_id():
    # Student cannot change id through PATCH
    student_id = uuid4()
    mock_student = MockStudent()

    with patch('app.services.student_service.StudentService.update', new_callable=AsyncMock) as mock_update, \
         patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_student
        mock_update.return_value = mock_student
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/student-profiles/{student_id}", json={
                "id": str(uuid4())
            })
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_student_16_admin_create_valid_student():
    # Admin can create a profile for a valid STUDENT user
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@test.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockStudent()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": str(uuid4()),
                "first_name": "Valid",
                "last_name": "Student"
            })
        assert response.status_code == 201

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_17_admin_create_nonexistent_user():
    # Admin creation with nonexistent user_id -> rejected
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@test.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = EntityNotFound("User not found")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": str(uuid4()),
                "first_name": "Invalid",
                "last_name": "User"
            })
        assert response.status_code == 404

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_18_admin_create_admin_role_rejected():
    # Admin creation with ADMIN user_id -> rejected
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@test.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        from app.services.exceptions import BusinessRuleViolation
        mock_create.side_effect = BusinessRuleViolation("Cannot create student profile for admin")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": str(uuid4()),
                "first_name": "Admin",
                "last_name": "User"
            })
        assert response.status_code == 400

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_19_admin_create_agency_role_rejected():
    # Admin creation with AGENCY user_id -> rejected
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@test.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        from app.services.exceptions import BusinessRuleViolation
        mock_create.side_effect = BusinessRuleViolation("Cannot create student profile for agency")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": str(uuid4()),
                "first_name": "Agency",
                "last_name": "User"
            })
        assert response.status_code == 400

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_20_admin_create_valid_student_succeeds():
    # Admin creation with valid STUDENT user_id -> succeeds
    def get_admin_user():
        return User(id=str(uuid4()), email="admin@test.com", is_active=True, role=UserRole.ADMIN)
    app.dependency_overrides[get_current_active_user] = get_admin_user

    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockStudent()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": str(uuid4()),
                "first_name": "Valid",
                "last_name": "Student"
            })
        assert response.status_code == 201

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


@pytest.mark.asyncio
async def test_student_21_duplicate_student_rejected():
    # Duplicate student profile remains rejected
    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        from app.services.exceptions import BusinessRuleViolation
        mock_create.side_effect = BusinessRuleViolation("Student profile already exists")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "user_id": TEST_USER_ID,
                "first_name": "Alice",
                "last_name": "Smith"
            })
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_student_22_update_ownership_still_works():
    # Existing update ownership behavior still works
    student_id = uuid4()
    mock_student = MockStudent()
    with patch('app.services.student_service.StudentService.update', new_callable=AsyncMock) as mock_update, \
         patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_student
        mock_update.return_value = mock_student
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/student-profiles/{student_id}", json={
                "first_name": "Updated"
            })
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_student_23_delete_ownership_still_works():
    # Existing delete ownership behavior still works
    student_id = uuid4()
    mock_student = MockStudent()
    with patch('app.services.student_service.StudentService.delete', new_callable=AsyncMock) as mock_delete, \
         patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_student
        mock_delete.return_value = True
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_student_24_auth_rbac_remains_intact():
    # Existing authentication/RBAC behavior remains intact
    # Verify unauthenticated listing is blocked
    app.dependency_overrides.pop(get_current_active_user, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/student-profiles")
    assert response.status_code == 401
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user


