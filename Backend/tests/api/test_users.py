import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import patch, AsyncMock, MagicMock
from app.dependencies.auth import get_current_active_user
from app.models.user import User

def override_get_current_active_user():
    return User(id="test", email="test@test.com", is_active=True, role="admin")

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

from uuid import uuid4

@pytest.mark.asyncio
async def test_get_all_users():
    class MockResult:
        def __init__(self):
            self.items = []
            self.total = 0
            self.page = 1
            self.page_size = 10
            self.total_pages = 0
            
    with patch('app.repositories.base.BaseRepository.list_paginated', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockResult()
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/users")
            
        assert response.status_code == 200
        assert "items" in response.json()["data"]

@pytest.mark.asyncio
async def test_get_single_user():
    user_id = uuid4()
    
    class MockUser:
        id = user_id
        email = "test@example.com"
        role = "student"
        is_active = True
        is_verified = True
        created_at = "2023-01-01T00:00:00Z"
        updated_at = "2023-01-01T00:00:00Z"
        last_login = None
        
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockUser()
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/users/{user_id}")
            
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_non_existing_user():
    user_id = uuid4()
    
    with patch('app.services.base.BaseService.get_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/users/{user_id}")
            
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_user():
    user_id = uuid4()
    
    class MockUser:
        id = user_id
        email = "test@example.com"
        role = "student"
        is_active = True
        is_verified = True
        created_at = "2023-01-01T00:00:00Z"
        updated_at = "2023-01-01T00:00:00Z"
        last_login = None
        
    with patch('app.services.base.BaseService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = MockUser()
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/users/{user_id}", json={
                "first_name": "John"
            })
            
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_email():
    user_id = uuid4()
    class MockUser:
        id = user_id
        email = "test@example.com"
        role = "student"
        is_active = True
        is_verified = True
        created_at = "2023-01-01T00:00:00Z"
        updated_at = "2023-01-01T00:00:00Z"
        last_login = None
    
    with patch('app.services.base.BaseService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = MockUser()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/users/{user_id}", json={
                "email": "new@example.com"
            })
            
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_deactivate_user():
    user_id = uuid4()
    
    with patch('app.services.base.BaseService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/users/{user_id}")
            
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_invalid_uuid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/users/invalid-uuid")
        
    assert response.status_code == 422
