from app.core.security import verify_password
from app.models.user import User
from app.services.user_service import UserService


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.user_service.get_by_email(email)
        if not user:
            return None

        if not user.is_active:
            return None
            
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        if user.locked_until and user.locked_until > now:
            return None
            
        from app.models.enums import AgencyVerificationStatus, UserRole
        if user.role == UserRole.AGENCY:
            from sqlalchemy import select

            from app.models.agency import Agency
            stmt = select(Agency).where(Agency.user_id == str(user.id))
            result = await self.user_service.repository.session.execute(stmt)
            agency = result.scalar_one_or_none()
            if agency and agency.verification_status == AgencyVerificationStatus.REJECTED:
                return None

        from typing import Any
        from uuid import UUID
        
        if not verify_password(password, user.password_hash):
            new_attempts = user.failed_login_attempts + 1
            update_data: dict[str, Any] = {"failed_login_attempts": new_attempts}
            if new_attempts >= 5:
                update_data["locked_until"] = now + timedelta(minutes=15)
            await self.user_service.update(UUID(str(user.id)), update_data)
            return None
            
        if user.failed_login_attempts > 0 or user.locked_until is not None:
            await self.user_service.update(UUID(str(user.id)), {"failed_login_attempts": 0, "locked_until": None})
            
        # Update last_login
        await self.user_service.update(UUID(str(user.id)), {"last_login": now})

        return user
