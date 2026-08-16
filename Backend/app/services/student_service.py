from typing import Any
from uuid import UUID

from app.models.student_profile import StudentProfile
from app.repositories.student_profile_repository import StudentProfileRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService
from app.services.exceptions import EntityNotFound


class StudentService(BaseService[StudentProfile, Any, Any]):
    repository: StudentProfileRepository
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

    def __init__(
        self,
        repository: StudentProfileRepository,
        transaction_manager: TransactionManager,
    ):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    def _to_model(self, obj_in: Any) -> StudentProfile:
        data = (
            obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, "model_dump")
            else obj_in
        )
        return StudentProfile(**data)

    async def _get_user_agency_id(self, user: Any) -> str | None:
        if not user:
            return None
        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        if role_str != "agency":
            return None
        if hasattr(user, "agency_profile") and user.agency_profile is not None:
            return str(user.agency_profile.id)
        try:
            from sqlalchemy import select

            from app.models.agency import Agency
            stmt = select(Agency).where(Agency.user_id == str(user.id))
            result = await self.repository.session.execute(stmt)
            agency = result.scalar_one_or_none()
            if agency:
                if hasattr(agency, "id"):
                    return str(agency.id)
                return str(agency)
        except Exception:  # noqa: BLE001, S110
            pass
        return None

    async def _check_read_visibility(self, student: StudentProfile, user: Any = None) -> None:
        from app.models.enums import UserRole
        from app.services.exceptions import PermissionDenied

        if user is None:
            raise PermissionDenied("You do not have permission to view this student profile.")

        if user.role == UserRole.ADMIN:
            return

        if user.role == UserRole.STUDENT:
            if str(student.user_id) != str(user.id):
                raise PermissionDenied("You do not have permission to view this student profile.")
            return

        if user.role == UserRole.AGENCY:
            agency_id = await self._get_user_agency_id(user)
            if not agency_id:
                raise PermissionDenied("You do not have permission to view this student profile.")
            
            from sqlalchemy import select

            from app.models.enums import LeadStatus
            from app.models.lead import Lead
            # Allow agency to view only if a lead exists linking them to this student and is active
            lead_stmt = select(Lead.id).where(
                Lead.student_id == str(student.id),
                Lead.agency_id == str(agency_id),
                Lead.status != LeadStatus.LOST
            )
            lead_res = await self.repository.session.execute(lead_stmt)
            if not lead_res.scalar_one_or_none():
                raise PermissionDenied("You do not have permission to view this student profile.")
            return

        raise PermissionDenied("You do not have permission to view this student profile.")

    async def get_by_id_scoped(self, id: UUID, user: Any = None) -> StudentProfile | None:
        student = await super().get_by_id(id)
        if not student:
            student = await self.get_by_user_id(id)
        if student and user:
            await self._check_read_visibility(student, user)
        return student

    async def get_by_user_id(self, user_id: UUID | str) -> StudentProfile | None:
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

            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else obj_in
            )
            # Prevent mass assignment of sensitive identifiers
            update_data.pop("user_id", None)
            update_data.pop("id", None)
            return await self.repository.update(profile.id, update_data)  # type: ignore

    async def list_student_profiles(self, user: Any, pagination: Any) -> Any:
        own_agency_id = await self._get_user_agency_id(user)
        return await self.repository.list_scoped(pagination, user.role, own_agency_id, str(user.id))

    async def create(self, obj_in: Any, user: Any = None) -> StudentProfile:
        async with self.transaction_manager.transaction():
            data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else dict(obj_in)
            
            from app.models.enums import UserRole
            from app.services.exceptions import BusinessRuleViolation, PermissionDenied
            
            if user is not None:
                if user.role != UserRole.ADMIN:
                    if user.role != UserRole.STUDENT:
                        raise PermissionDenied("Only students can create student profiles.")
                    # Force student's own user_id
                    data["user_id"] = str(user.id)
                else:
                    # Admin must specify a valid user_id
                    target_user_id = data.get("user_id")
                    if not target_user_id:
                        raise BusinessRuleViolation("Admin must specify user_id when creating a student profile.")
                    
                    from sqlalchemy import select

                    from app.models.user import User as DBUser
                    user_stmt = select(DBUser).where(DBUser.id == str(target_user_id))
                    user_res = await self.repository.session.execute(user_stmt)
                    target_user = user_res.scalar_one_or_none()
                    if not target_user:
                        raise EntityNotFound(f"User with ID {target_user_id} not found.")
                    if target_user.role != UserRole.STUDENT:
                        raise BusinessRuleViolation("Cannot create a student profile for a non-student user.")
            else:
                # Fallback / unit test behavior
                user_id = data.get("user_id")
                if not user_id:
                    raise EntityNotFound("Related user not found")

            # Check if profile already exists for the resolved user_id
            resolved_user_id = data.get("user_id")
            if not resolved_user_id:
                raise BusinessRuleViolation("user_id is required")
            existing = await self.repository.get_by_user_id(str(resolved_user_id))
            if existing:
                raise BusinessRuleViolation("Student profile already exists for this user")
            
            model_instance = self._to_model(data)
            return await self.repository.create(model_instance)

    async def update(self, id: UUID, obj_in: Any, user: Any = None) -> StudentProfile | None:
        async with self.transaction_manager.transaction():
            student = await self._require_entity(id)
            if user is not None:
                from app.models.enums import UserRole
                if user.role != UserRole.ADMIN and str(student.user_id) != str(user.id):
                    from app.services.exceptions import PermissionDenied
                    raise PermissionDenied("You do not have permission to update this student profile.")
            
            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else dict(obj_in)
            )
            # Prevent mass assignment of sensitive identifiers
            update_data.pop("user_id", None)
            update_data.pop("id", None)
            return await self.repository.update(id, update_data)
            
    async def delete(self, id: UUID, user: Any = None) -> bool:
        async with self.transaction_manager.transaction():
            student = await self._require_entity(id)
            if user is not None:
                from app.models.enums import UserRole
                if user.role != UserRole.ADMIN and str(student.user_id) != str(user.id):
                    from app.services.exceptions import PermissionDenied
                    raise PermissionDenied("You do not have permission to delete this student profile.")
            return await self.repository.delete(id)
