from typing import Any
from uuid import UUID

from app.models.user import User
from app.repositories.transaction import TransactionManager
from app.repositories.user_repository import UserRepository
from app.services.base import BaseService


class UserService(BaseService[User, Any, Any]):
    repository: UserRepository
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

    def __init__(
        self, repository: UserRepository, transaction_manager: TransactionManager
    ):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    def _to_model(self, obj_in: Any) -> User:
        data = (
            obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, "model_dump")
            else obj_in.copy() if isinstance(obj_in, dict) else dict(obj_in)
        )

        # Domain mapping: extract plain-text password, hash it, and store in password_hash
        if "password" in data:
            password = data.pop("password")

            # Using the project's existing password hashing utility
            try:
                from app.core.security import get_password_hash

                data["password_hash"] = get_password_hash(password)
            except ImportError:
                # Fallback in case the security module is located elsewhere or not yet merged
                import hashlib

                data["password_hash"] = hashlib.sha256(password.encode()).hexdigest()

        return User(**data)

    async def get_by_email(self, email: str) -> User | None:
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
            self._prevent_redundant_state(
                user.is_active, True, f"User {id} is already active."
            )
            return await self.repository.update(id, {"is_active": True})  # type: ignore

    async def deactivate(self, id: UUID) -> User:
        """
        Deactivate a user account.
        Raises BusinessRuleViolation if already inactive.
        """
        async with self.transaction_manager.transaction():
            user = await self._require_entity(id)
            self._prevent_redundant_state(
                user.is_active, False, f"User {id} is already inactive."
            )
            return await self.repository.update(id, {"is_active": False})  # type: ignore

    async def create(self, obj_in: Any) -> User:
        async with self.transaction_manager.transaction():
            data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in
            if await self.email_exists(data.get("email")):
                from app.services.exceptions import BusinessRuleViolation
                raise BusinessRuleViolation("Email already exists")
            if data.get("role") not in ["student", "agency", "admin"]:
                from app.services.exceptions import BusinessRuleViolation
                raise BusinessRuleViolation("Invalid role")
            model_instance = self._to_model(obj_in)
            created_user = await self.repository.create(model_instance)
            
            import uuid
            role_val = data.get("role")
            if role_val and (role_val == "student" or role_val == "STUDENT"):
                from app.models.student_profile import StudentProfile
                sp = StudentProfile(
                    id=str(uuid.uuid4()),
                    user_id=created_user.id,
                    first_name="New",
                    last_name="Student"
                )
                self.transaction_manager.session.add(sp)
            elif role_val and (role_val == "agency" or role_val == "AGENCY"):
                from app.models.agency import Agency
                email_prefix = data.get("email", "Agency").split("@")[0]
                ap = Agency(
                    id=str(uuid.uuid4()),
                    user_id=created_user.id,
                    agency_name=email_prefix,
                    email=data.get("email")
                )
                self.transaction_manager.session.add(ap)
                
            return created_user

    async def update(self, id: UUID, obj_in: Any, user: Any = None) -> User | None:
        async with self.transaction_manager.transaction():
            user_obj = await self._require_entity(id)
            if user is not None:
                from app.models.enums import UserRole
                if user.role != UserRole.ADMIN and str(user_obj.id) != str(user.id):
                    from app.services.exceptions import PermissionDenied
                    raise PermissionDenied("You do not have permission to update this user.")
            
            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else obj_in.copy() if isinstance(obj_in, dict) else dict(obj_in)
            )

            # Prevent non-admin from modifying is_active
            if user is not None:
                from app.models.enums import UserRole
                if user.role != UserRole.ADMIN:
                    update_data.pop("is_active", None)

            return await self.repository.update(id, update_data)

    async def delete(self, id: UUID, user: Any = None) -> bool:
        async with self.transaction_manager.transaction():
            await self._require_entity(id)
            if user is not None:
                from app.models.enums import UserRole
                if user.role != UserRole.ADMIN:
                    from app.services.exceptions import PermissionDenied
                    raise PermissionDenied("Only admin users can delete users.")
                    
            return await self.repository.delete(id)
