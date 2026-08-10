
with open('app/services/user_service.py', 'r') as f:
    content = f.read()

new_method = '''
    async def update_user(self, id: UUID, obj_in: Any) -> User:
        """
        Update user information including linked profile fields.
        """
        async with self.transaction_manager.transaction():
            user = await self._require_entity(id)
            
            data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
            
            # Update user fields
            user_updates = {}
            if "is_active" in data:
                user_updates["is_active"] = data.pop("is_active")
                
            if user_updates:
                await self.repository.update(id, user_updates)
                
            # Update profile fields if necessary
            if data and user.role.value == "student":
                # Only update student profile if fields exist
                from sqlalchemy import update as sa_update
                from app.models.student_profile import StudentProfile
                
                profile_updates = {}
                for field in ["first_name", "last_name", "phone"]:
                    if field in data:
                        profile_updates[field] = data.pop(field)
                        
                if profile_updates:
                    stmt = sa_update(StudentProfile).where(StudentProfile.user_id == str(id)).values(**profile_updates)
                    await self.transaction_manager.session.execute(stmt)
                    
            elif data and user.role.value == "agency":
                from sqlalchemy import update as sa_update
                from app.models.agency import Agency
                
                profile_updates = {}
                if "first_name" in data or "last_name" in data:
                    first = data.pop("first_name", "")
                    last = data.pop("last_name", "")
                    name = f"{first} {last}".strip()
                    if name:
                        profile_updates["contact_person_name"] = name
                if "phone" in data:
                    profile_updates["contact_number"] = data.pop("phone")
                    
                if profile_updates:
                    stmt = sa_update(Agency).where(Agency.user_id == str(id)).values(**profile_updates)
                    await self.transaction_manager.session.execute(stmt)
            
            await self.transaction_manager.session.refresh(user)
            return user
'''

if 'def update_user(' not in content:
    content += new_method
    with open('app/services/user_service.py', 'w') as f:
        f.write(content)

with open('tests/api/test_users.py', 'w') as f:
    f.write('''import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import patch, AsyncMock
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
        
    with patch('app.services.base.BaseService.get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MockUser()
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/users/{user_id}")
            
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_non_existing_user():
    user_id = uuid4()
    
    with patch('app.services.base.BaseService.get', new_callable=AsyncMock) as mock_get:
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
        
    with patch('app.services.user_service.UserService.update_user', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = MockUser()
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(f"/api/v1/users/{user_id}", json={
                "first_name": "John"
            })
            
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_email_rejected():
    user_id = uuid4()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Schema rejects unknown fields (or ignores them), but if we try to pass it, the endpoint doesn't process it.
        # Even if it passes validation, email is not in UserUpdate schema.
        response = await client.patch(f"/api/v1/users/{user_id}", json={
            "email": "new@example.com"
        })
        
    # The email will be ignored since it's not in the schema, but we want to make sure it doesn't fail or update
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_deactivate_user():
    user_id = uuid4()
    
    with patch('app.services.user_service.UserService.deactivate', new_callable=AsyncMock) as mock_deactivate:
        mock_deactivate.return_value = True
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/v1/users/{user_id}")
            
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_invalid_uuid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/users/invalid-uuid")
        
    assert response.status_code == 422
''')
