from typing import Any, Optional
from uuid import UUID

from app.models.student_profile import StudentProfile
from app.repositories.student_profile_repository import StudentProfileRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService
from app.services.exceptions import EntityNotFound


class StudentService(BaseService[StudentProfile, Any, Any]):
    """
    Business Responsibility:
    Handles student profile data management and existence verification.
    
    Does:
    - Update student profile information.
    - Retrieve and verify profile existence by user ID.
    
    Does Not:
    - Handle core authentication or password management (UserService).
    
    Dependencies:
    - StudentProfileRepository for data access.
    
    Transaction Behaviour:
    - Read operations (get_by_user_id, profile_exists) do not use transactions.
    - Mutating operations (update_profile) are enclosed within TransactionManager.
    """

    def __init__(self, repository: StudentProfileRepository, transaction_manager: TransactionManager):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    async def get_by_user_id(self, user_id: UUID | str) -> Optional[StudentProfile]:
        """
        Retrieve a student profile by the associated user ID.
        """
        return await self.repository.get_by_user_id(user_id)

    async def profile_exists(self, user_id: UUID | str) -> bool:
        """
        Check if a student profile exists for the given user ID.
        """
        profile = await self.get_by_user_id(user_id)
        return profile is not None

    async def update_profile(self, user_id: UUID | str, obj_in: Any) -> StudentProfile:
        """
        Update a student profile based on user ID.
        Raises EntityNotFound if the profile does not exist.
        """
        async with self.transaction_manager.transaction():
            profile = await self.get_by_user_id(user_id)
            if not profile:
                raise EntityNotFound(f"Student profile for user {user_id} not found.")
            
            update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
            return await self.repository.update(profile.id, update_data)  # type: ignore
