import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.exceptions import EntityNotFound, BusinessRuleViolation

def override_get_current_active_user():
    return User(id=str(uuid4()), email="test@test.com", is_active=True, role="student")

# We apply the override globally for these tests
app.dependency_overrides[get_current_active_user] = override_get_current_active_user

class MockStudent:
    def __init__(self):
        self.id = uuid4()
        self.user_id = uuid4()
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
                "first_name": "Alice",
                "last_name": "Smith",
                "user_id": str(uuid4())
            })
        assert response.status_code == 201
        assert response.json()["data"]["first_name"] == "Alice"

@pytest.mark.asyncio
async def test_duplicate_student():
    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Student profile already exists for this user")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "first_name": "Alice",
                "last_name": "Smith",
                "user_id": str(uuid4())
            })
        assert response.status_code == 400
        assert "already exists" in str(response.json())

@pytest.mark.asyncio
async def test_invalid_user_create():
    with patch('app.services.student_service.StudentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = EntityNotFound("Related user not found")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/student-profiles", json={
                "first_name": "Alice",
                "last_name": "Smith",
                "user_id": str(uuid4())
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
            
    with patch('app.repositories.base.BaseRepository.list_paginated', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockResult()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/student-profiles")
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
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_student():
    student_id = uuid4()
    with patch('app.services.base.BaseService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = MockStudent()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/student-profiles/{student_id}", json={
                "first_name": "Bob"
            })
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_student():
    student_id = uuid4()
    with patch('app.services.base.BaseService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_invalid_student():
    student_id = uuid4()
    with patch('app.services.base.BaseService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.side_effect = EntityNotFound("Not found")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/student-profiles/{student_id}")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_unauthorized_access():
    app.dependency_overrides.clear()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/student-profiles")
    assert response.status_code == 401
    
    # restore override for other tests if needed
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
