from app.core.security import verify_password
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
