from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_register_user():
    with patch('app.services.user_service.UserService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = True
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/register", json={
                "email": "test@example.com",
                "password": "password123",
                "role": "student"
            })
        assert response.status_code == 201

@pytest.mark.asyncio
async def test_login_user():
    class MockUser:
        id = "00000000-0000-0000-0000-000000000001"
        email = "test@example.com"
        role = "student"
        password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq" # valid bcrypt hash for "password123"
        is_active = True
        locked_until = None
        failed_login_attempts = 0
        last_login = None
        
    with patch('app.services.user_service.UserService.get_by_email', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockUser()
        with patch('app.services.auth_service.verify_password', return_value=True), \
             patch('app.services.user_service.UserService.update', new_callable=AsyncMock):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    response = await client.post("/api/v1/auth/login", data={
                        "username": "test@example.com",
                        "password": "password123"
                    })
                assert response.status_code == 200
                assert "access_token" in response.json()
