from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.dependencies.services import get_auth_service, get_user_service
from app.schemas.auth import Token, UserCreate
from app.services.auth_service import AuthService
from app.services.exceptions import BusinessRuleViolation
from app.services.user_service import UserService

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
        data={"sub": user.email, "role": user.role, "id": str(user.id)}, expires_delta=access_token_expires
    )
    
    from app.core.security import create_refresh_token
    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": str(user.id)}
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

from pydantic import BaseModel


class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: RefreshRequest,
    user_service: UserService = Depends(get_user_service)
):
    from datetime import datetime, timezone

    import jwt
    from jwt.exceptions import InvalidTokenError

    from app.core.security import ALGORITHM, SECRET_KEY

    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")
        iat = payload.get("iat")
        if email is None or token_type != "refresh" or iat is None:
            raise InvalidTokenError()
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = await user_service.get_by_email(email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    now = datetime.now(timezone.utc)
    if user.locked_until and user.locked_until > now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    from app.models.enums import AgencyVerificationStatus, UserRole
    if user.role == UserRole.AGENCY:
        from sqlalchemy import select

        from app.models.agency import Agency
        stmt = select(Agency).where(Agency.user_id == str(user.id))
        result = await user_service.repository.session.execute(stmt)
        agency = result.scalar_one_or_none()
        if agency and agency.verification_status == AgencyVerificationStatus.REJECTED:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Check for revocation globally using password_changed_at
    # If the user changed their password AFTER the token was issued, the token is revoked.
    token_iat = datetime.fromtimestamp(iat, tz=timezone.utc)
    if user.password_changed_at and token_iat < user.password_changed_at.astimezone(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked")

    # Issue new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": str(user.id)}, expires_delta=access_token_expires
    )
    from app.core.security import create_refresh_token
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": str(user.id)}
    )
    
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    if user_in.role.lower() == "admin":
        raise HTTPException(status_code=400, detail="Cannot register admin user publicly.")
    try:
        await user_service.create(user_in)
    except BusinessRuleViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "User registered successfully"}
