from typing import Any, Optional
from uuid import UUID

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService
from app.services.exceptions import BusinessRuleViolation


class UserService(BaseService[User, Any, Any]):
    """
    Business Responsibility:
    Handles core user lifecycle management, including fetching user details and toggling active status.
    
    Does:
    - Retrieve user records by email.
    - Toggle user account activation status.
    
    Does Not:
    - Handle passwords, hashing, or JWT authentication (delegated to auth services).
    
    Dependencies:
    - UserRepository for data access.
    
    Transaction Behaviour:
    - Read operations (get_by_email, email_exists) do not use transactions.
    - Mutating operations (activate, deactivate) are enclosed within TransactionManager.
    """

    def __init__(self, repository: UserRepository, transaction_manager: TransactionManager):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        """
        return await self.repository.get_by_email(email)

    async def email_exists(self, email: str) -> bool:
        """
        Check if a user exists with the given email.
        """
        user = await self.get_by_email(email)
        return user is not None

    async def activate(self, id: UUID) -> User:
        """
        Activate a user account.
        Raises BusinessRuleViolation if already active.
        """
        async with self.transaction_manager.transaction():
            user = await self._require_entity(id)
            self._prevent_redundant_state(user.is_active, True, f"User {id} is already active.")
            return await self.repository.update(id, {"is_active": True})  # type: ignore

    async def deactivate(self, id: UUID) -> User:
        """
        Deactivate a user account.
        Raises BusinessRuleViolation if already inactive.
        """
        async with self.transaction_manager.transaction():
            user = await self._require_entity(id)
            self._prevent_redundant_state(user.is_active, False, f"User {id} is already inactive.")
            return await self.repository.update(id, {"is_active": False})  # type: ignore
