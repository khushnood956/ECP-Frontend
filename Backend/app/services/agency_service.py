from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.models.agency import Agency
from app.models.enums import AgencyVerificationStatus
from app.repositories.agency_repository import AgencyRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService


class AgencyService(BaseService[Agency, Any, Any]):
    repository: AgencyRepository
    """
    Business Responsibility:
    Handles educational agency profile operations and verification lifecycle.

    Does:
    - Verify and suspend agencies.
    - Retrieve agencies by registration number.

    Does Not:
    - Manage standard user creation (handled by UserService).

    Dependencies:
    - AgencyRepository for data access.

    Transaction Behaviour:
    - Read operations (get_by_registration_number) do not use transactions.
    - Mutating operations (verify_agency, suspend_agency) are enclosed within TransactionManager.
    """

    def __init__(
        self, repository: AgencyRepository, transaction_manager: TransactionManager
    ):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    def _to_model(self, obj_in: Any) -> Agency:
        data = (
            obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, "model_dump")
            else obj_in
        )
        return Agency(**data)

    def _check_read_visibility(self, agency: Agency, user: Any = None) -> None:
        from app.models.enums import AgencyVerificationStatus, UserRole
        if agency.verification_status == AgencyVerificationStatus.VERIFIED:
            return
            
        if user is not None:
            if user.role == UserRole.ADMIN:
                return
            if str(agency.user_id) == str(user.id):
                return
                
        from app.services.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to view this agency profile.")

    async def get_by_id(self, id: UUID, user: Any = None) -> Agency | None:
        agency = await super().get_by_id(id)
        if agency:
            self._check_read_visibility(agency, user)
        return agency

    async def get_by_user_id(self, user_id: UUID | str, user: Any = None) -> Agency | None:
        agency = await self.repository.get_by_user_id(user_id)
        if agency:
            self._check_read_visibility(agency, user)
        return agency

    async def get_by_registration_number(
        self, registration_number: str, user: Any = None
    ) -> Agency | None:
        """
        Retrieve an agency by its registration number.
        """
        agency = await self.repository.get_by_registration_number(registration_number)
        if agency:
            self._check_read_visibility(agency, user)
        return agency

    async def verify_agency(self, id: UUID) -> Agency:
        """
        Verify an agency.
        Raises BusinessRuleViolation if already verified.
        """
        async with self.transaction_manager.transaction():
            agency = await self._require_entity(id)
            self._prevent_redundant_state(
                agency.verification_status,
                AgencyVerificationStatus.VERIFIED,
                f"Agency {id} is already verified.",
            )

            update_data = {
                "verification_status": AgencyVerificationStatus.VERIFIED,
                "verified_at": datetime.now(timezone.utc),
            }
            return await self.repository.update(id, update_data)  # type: ignore

    async def suspend_agency(self, id: UUID) -> Agency:
        """
        Suspend an agency by marking its verification status as rejected.
        Raises BusinessRuleViolation if already suspended/rejected.
        """
        async with self.transaction_manager.transaction():
            agency = await self._require_entity(id)
            self._prevent_redundant_state(
                agency.verification_status,
                AgencyVerificationStatus.REJECTED,
                f"Agency {id} is already suspended.",
            )

            update_data = {"verification_status": AgencyVerificationStatus.REJECTED}
            return await self.repository.update(id, update_data)  # type: ignore

    async def create(self, obj_in: Any, user: Any = None) -> Agency:
        from app.models.enums import UserRole
        if user is None or user.role != UserRole.AGENCY:
            from app.services.exceptions import PermissionDenied
            raise PermissionDenied("Only agency users can create agency profiles.")

        existing_user_agency = await self.repository.get_by_user_id(user.id)
        if existing_user_agency:
            from app.services.exceptions import EntityAlreadyExists
            raise EntityAlreadyExists("This user already has an agency profile.")

        async with self.transaction_manager.transaction():
            data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else dict(obj_in)
            reg_num = data.get("registration_number")
            if reg_num:
                existing = await self.repository.get_by_registration_number(reg_num)
                if existing:
                    from app.services.exceptions import EntityAlreadyExists
                    raise EntityAlreadyExists(f"Agency with registration number '{reg_num}' already exists.")
            data["user_id"] = str(user.id)
            model_instance = self._to_model(data)
            return await self.repository.create(model_instance)


    async def update(self, id: UUID, obj_in: Any, user: Any = None) -> Agency | None:
        async with self.transaction_manager.transaction():
            agency = await self._require_entity(id)
            if user is not None:
                from app.models.enums import UserRole
                if user.role != UserRole.ADMIN and str(agency.user_id) != str(user.id):
                    from app.services.exceptions import PermissionDenied
                    raise PermissionDenied("You do not have permission to update this agency.")

            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else dict(obj_in)
            )

            new_reg_num = update_data.get("registration_number")
            if new_reg_num and new_reg_num != agency.registration_number:
                existing = await self.repository.get_by_registration_number(new_reg_num)
                if existing and existing.id != id:
                    from app.services.exceptions import EntityAlreadyExists
                    raise EntityAlreadyExists(f"Agency with registration number '{new_reg_num}' already exists.")

            return await self.repository.update(id, update_data)

    async def delete(self, id: UUID, user: Any = None) -> bool:
        async with self.transaction_manager.transaction():
            agency = await self._require_entity(id)
            if user is not None:
                from app.models.enums import UserRole
                if user.role != UserRole.ADMIN and str(agency.user_id) != str(user.id):
                    from app.services.exceptions import PermissionDenied
                    raise PermissionDenied("You do not have permission to delete this agency.")
            return await self.repository.delete(id)

