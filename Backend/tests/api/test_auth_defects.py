from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import ALGORITHM, SECRET_KEY, get_password_hash
from app.models.enums import AgencyVerificationStatus, UserRole
from app.models.user import User
from main import app


class MockUser(User):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'failed_login_attempts' not in kwargs:
            self.failed_login_attempts = 0
        if 'locked_until' not in kwargs:
            self.locked_until = None
        if 'last_login' not in kwargs:
            self.last_login = None
        if 'password_changed_at' not in kwargs:
            self.password_changed_at = None

def get_mock_active_user():
    return MockUser(
        id="00000000-0000-0000-0000-000000000001",
        email="active@test.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.STUDENT,
        is_active=True
    )

def get_mock_inactive_user():
    return MockUser(
        id="00000000-0000-0000-0000-000000000002",
        email="inactive@test.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.STUDENT,
        is_active=False
    )

def get_mock_rejected_agency_user():
    return MockUser(
        id="00000000-0000-0000-0000-000000000003",
        email="rejected@agency.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.AGENCY,
        is_active=True
    )

@pytest.fixture
def mock_user_service():
    with patch('app.dependencies.services.UserService', autospec=True) as MockUserService:
        service = MockUserService.return_value
        yield service

@pytest.mark.asyncio
async def test_auth_01_active_user_login_succeeds():
    user = get_mock_active_user()
    with patch('app.services.user_service.UserService.get_by_email', new_callable=AsyncMock) as mock_get, \
         patch('app.services.user_service.UserService.update', new_callable=AsyncMock):
            mock_get.return_value = user
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/api/v1/auth/login", data={"username": "active@test.com", "password": "password123"})
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

@pytest.mark.asyncio
async def test_auth_02_inactive_user_login_rejected():
    user = get_mock_inactive_user()
    with patch('app.services.user_service.UserService.get_by_email', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = user
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", data={"username": "inactive@test.com", "password": "password123"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_auth_03_04_rejected_and_suspended_agency_login_rejected():
    user = get_mock_rejected_agency_user()
    class MockAgency:
        verification_status = AgencyVerificationStatus.REJECTED
    
    with patch('app.services.user_service.UserService.get_by_email', new_callable=AsyncMock) as mock_get, \
         patch('sqlalchemy.ext.asyncio.AsyncSession.execute', new_callable=AsyncMock) as mock_execute:
            mock_get.return_value = user
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = MockAgency()
            mock_execute.return_value = mock_result
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/api/v1/auth/login", data={"username": "rejected@agency.com", "password": "password123"})
            assert response.status_code == 401

@pytest.mark.asyncio
async def test_auth_05_06_07_failed_login_handling():
    user = get_mock_active_user()
    user.failed_login_attempts = 4
    
    with patch('app.services.user_service.UserService.get_by_email', new_callable=AsyncMock) as mock_get, \
         patch('app.services.user_service.UserService.update', new_callable=AsyncMock) as mock_update:
            mock_get.return_value = user
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                # AUTH-05: wrong password
                response = await client.post("/api/v1/auth/login", data={"username": "active@test.com", "password": "wrong"})
                assert response.status_code == 401
                # Should update failed_login_attempts to 5 and set locked_until
                update_kwargs = mock_update.call_args.args[1]
                assert update_kwargs["failed_login_attempts"] == 5
                assert "locked_until" in update_kwargs
                
                # Mock it being locked
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=10)
                
                # AUTH-06: locked account is rejected even with right password
                response2 = await client.post("/api/v1/auth/login", data={"username": "active@test.com", "password": "password123"})
                assert response2.status_code == 401
                
                # AUTH-07: unlock and successful login resets counter
                user.locked_until = None
                user.failed_login_attempts = 5
                response3 = await client.post("/api/v1/auth/login", data={"username": "active@test.com", "password": "password123"})
                assert response3.status_code == 200
                reset_update_kwargs = mock_update.call_args_list[-2].args[1]
                assert reset_update_kwargs["failed_login_attempts"] == 0

@pytest.mark.asyncio
async def test_auth_08_09_10_11_refresh_token_behavior():
    user = get_mock_active_user()
    user.password_changed_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    
    with patch('app.services.user_service.UserService.get_by_email', new_callable=AsyncMock) as mock_get, \
         patch('app.services.user_service.UserService.update', new_callable=AsyncMock):
        mock_get.return_value = user
        
        # Login
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", data={"username": "active@test.com", "password": "password123"})
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data # AUTH-08
            
            refresh_token = data["refresh_token"]
            
            # Use refresh token (AUTH-09)
            refresh_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
            assert refresh_resp.status_code == 200
            refresh_data = refresh_resp.json()
            assert "access_token" in refresh_data
            assert "refresh_token" in refresh_data
            
            # Simulate revocation by updating password_changed_at past the token's iat
            # The token was issued at time T. We set password_changed_at to T + 10s
            user.password_changed_at = datetime.now(timezone.utc) + timedelta(seconds=10)
            
            # Try reusing old refresh token (AUTH-10)
            revoked_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
            assert revoked_resp.status_code == 401
            
            # Try expired refresh token (AUTH-11)
            expired_token = jwt.encode({"sub": user.email, "type": "refresh", "exp": datetime.now(timezone.utc) - timedelta(days=1), "iat": datetime.now(timezone.utc) - timedelta(days=2)}, SECRET_KEY, algorithm=ALGORITHM)
            exp_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": expired_token})
            assert exp_resp.status_code == 401

@pytest.mark.asyncio
async def test_auth_12_inactive_user_cannot_refresh():
    user = get_mock_inactive_user()
    valid_token = jwt.encode({"sub": user.email, "type": "refresh", "exp": datetime.now(timezone.utc) + timedelta(days=1), "iat": datetime.now(timezone.utc)}, SECRET_KEY, algorithm=ALGORITHM)
    
    with patch('app.services.user_service.UserService.get_by_email', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = user
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/refresh", json={"refresh_token": valid_token})
        assert response.status_code == 401
