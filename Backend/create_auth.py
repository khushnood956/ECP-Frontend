import os

# Create security.py
os.makedirs('app/core', exist_ok=True)
with open('app/core/security.py', 'w') as f:
    f.write('''import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
''')

# Create auth dependencies (RBAC)
os.makedirs('app/dependencies', exist_ok=True)
with open('app/dependencies/auth.py', 'w') as f:
    f.write('''from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.auth import TokenPayload
from app.dependencies.services import get_user_service
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], user_service: Annotated[UserService, Depends(get_user_service)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None:
            raise credentials_exception
        token_data = TokenPayload(sub=email, role=role)
    except InvalidTokenError:
        raise credentials_exception
        
    user = await user_service.get_by_email(token_data.sub)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class RequireRole:
    def __init__(self, required_roles: list[str]):
        self.required_roles = required_roles

    def __call__(self, current_user = Depends(get_current_active_user)):
        if current_user.role not in self.required_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
''')

# Create auth schema
os.makedirs('app/schemas', exist_ok=True)
with open('app/schemas/auth.py', 'w') as f:
    f.write('''from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str | None = None
    role: str | None = None

class Login(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "student"
''')

# Create auth service
os.makedirs('app/services', exist_ok=True)
with open('app/services/auth_service.py', 'w') as f:
    f.write('''from app.core.security import verify_password
from app.services.exceptions import BusinessRuleViolation
from app.services.user_service import UserService
from app.models.user import User

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.user_service.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
''')

# Create auth dependencies in services.py
with open('app/dependencies/services.py', 'r') as f:
    services_content = f.read()

if 'get_auth_service' not in services_content:
    services_content += '''\nfrom app.services.auth_service import AuthService
async def get_auth_service(user_service=Depends(get_user_service)) -> AuthService:
    return AuthService(user_service=user_service)
'''
    with open('app/dependencies/services.py', 'w') as f:
        f.write(services_content)

# Create auth router
os.makedirs('app/api/v1', exist_ok=True)
with open('app/api/v1/auth.py', 'w') as f:
    f.write('''from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import Token, UserCreate
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.dependencies.services import get_auth_service, get_user_service
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.exceptions import BusinessRuleViolation

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.create(user_in)
    except BusinessRuleViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "User registered successfully"}
''')

# Register router
with open('app/api/router.py', 'r') as f:
    router_content = f.read()

if 'auth.router' not in router_content:
    router_content = router_content.replace('from app.api.v1 import ', 'from app.api.v1 import auth, ')
    router_content += '\napi_router.include_router(auth.router, prefix="/auth", tags=["Auth"])\n'
    with open('app/api/router.py', 'w') as f:
        f.write(router_content)

# Add Tests
os.makedirs('tests/api', exist_ok=True)
with open('tests/api/test_auth.py', 'w') as f:
    f.write('''import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient, mocker):
    mocker.patch('app.services.user_service.UserService.create', return_value=True)
    response = await async_client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "role": "student"
    })
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient, mocker):
    class MockUser:
        email = "test@example.com"
        role = "student"
        password_hash = "hashed"
        
    mocker.patch('app.services.user_service.UserService.get_by_email', return_value=MockUser())
    mocker.patch('app.core.security.verify_password', return_value=True)
    
    response = await async_client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
''')
