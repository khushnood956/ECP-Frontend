from datetime import timedelta
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
