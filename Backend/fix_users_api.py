import os

# 1. Update app/schemas/user.py
with open('app/schemas/user.py', 'r') as f:
    schema = f.read()

schema = schema.replace(
    '    first_name: str | None = None\n    last_name: str | None = None\n    phone: str | None = None',
    '    email: EmailStr | None = None'
)
with open('app/schemas/user.py', 'w') as f:
    f.write(schema)


# 2. Update app/services/user_service.py
with open('app/services/user_service.py', 'r') as f:
    service = f.read()

# I will replace `update_user` with just calling `self.update` from BaseService, 
# or completely remove `update_user` and change router to use `service.update`.
service_lines = service.split('\n')
new_service = []
skip = False
for line in service_lines:
    if line.startswith('    async def update_user(self, id: UUID, obj_in: Any) -> User:'):
        skip = True
    if skip and line.startswith('    ') and not line.startswith('        ') and not line.startswith('    async def update_user'):
        skip = False
    
    if not skip:
        new_service.append(line)

with open('app/services/user_service.py', 'w') as f:
    f.write('\n'.join(new_service))


# 3. Update app/api/v1/users.py
with open('app/api/v1/users.py', 'r') as f:
    router = f.read()

router = router.replace('from app.schemas.user import UserCreate, UserResponse, UserUpdate, PaginatedUserResponse\n', 
                        'from app.schemas.user import UserCreate, UserResponse, UserUpdate, PaginatedUserResponse\nfrom app.dependencies.auth import get_current_active_user\nfrom app.models.user import User\n')

# add dependencies to router routes
router = router.replace('async def get_users(\n', 'async def get_users(\n    current_user: User = Depends(get_current_active_user),\n')
router = router.replace('async def get_user(id: UUID, service: UserService = Depends(get_user_service)):', 'async def get_user(id: UUID, current_user: User = Depends(get_current_active_user), service: UserService = Depends(get_user_service)):')
router = router.replace('async def update_user(\n    id: UUID, user_in: UserUpdate, service: UserService = Depends(get_user_service)\n):', 'async def update_user(\n    id: UUID, user_in: UserUpdate, current_user: User = Depends(get_current_active_user), service: UserService = Depends(get_user_service)\n):')
router = router.replace('async def delete_user(id: UUID, service: UserService = Depends(get_user_service)):', 'async def delete_user(id: UUID, current_user: User = Depends(get_current_active_user), service: UserService = Depends(get_user_service)):')

# replace update_user call in router
router = router.replace('user = await service.update_user(id, user_in)', 'user = await service.update(id, user_in)')

# fix delete endpoint to actually delete
router_lines = router.split('\n')
new_router_lines = []
in_delete = False
for line in router_lines:
    if 'async def delete_user' in line:
        in_delete = True
        new_router_lines.append(line)
        new_router_lines.append('    from app.services.exceptions import EntityNotFound')
        new_router_lines.append('    try:')
        new_router_lines.append('        await service.delete(id)')
        new_router_lines.append('    except EntityNotFound as e:')
        new_router_lines.append('        raise HTTPException(status_code=404, detail=str(e))')
        new_router_lines.append('    return success_response(message="User deleted successfully")')
        continue
    
    if in_delete:
        if line.startswith('@'):
            in_delete = False
        else:
            continue
            
    if not in_delete:
        new_router_lines.append(line)

with open('app/api/v1/users.py', 'w') as f:
    f.write('\n'.join(new_router_lines))


# 4. Fix tests
with open('tests/api/test_users.py', 'r') as f:
    tests = f.read()

tests = tests.replace('from unittest.mock import patch, AsyncMock', 'from unittest.mock import patch, AsyncMock, MagicMock\nfrom app.dependencies.auth import get_current_active_user\nfrom app.models.user import User\n\ndef override_get_current_active_user():\n    return User(id="test", email="test@test.com", is_active=True, role="admin")\n\napp.dependency_overrides[get_current_active_user] = override_get_current_active_user\n')

# remove test_update_email_rejected logic and change to valid update
tests = tests.replace('test_update_email_rejected', 'test_update_email')
tests = tests.replace('assert response.status_code == 200', 'assert response.status_code == 200') # keep 200
tests = tests.replace("app.services.user_service.UserService.update_user", "app.services.base.BaseService.update")

with open('tests/api/test_users.py', 'w') as f:
    f.write(tests)
