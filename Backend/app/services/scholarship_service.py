from collections.abc import Sequence
from typing import Any
from uuid import UUID

from app.models.scholarship import Scholarship
from app.repositories.params import PaginatedResult, PaginationParams
from app.repositories.scholarship_repository import ScholarshipRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService


class ScholarshipService(BaseService[Scholarship, Any, Any]):
    """
    Business Responsibility:
    Handles scholarship publishing lifecycle and specialized search logic.

    Does:
    - Publish and unpublish scholarships.
    - Provide access to paginated and filtered scholarship searches.

    Does Not:
    - Handle lead generation or application tracking.

    Dependencies:
    - ScholarshipRepository for data access.

    Transaction Behaviour:
    - Read operations (search, active_scholarships) do not use transactions.
    - Mutating operations (publish, unpublish) are enclosed within TransactionManager.
    """

    def __init__(
        self, repository: ScholarshipRepository, transaction_manager: TransactionManager
    ):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    def _to_model(self, obj_in: Any) -> Scholarship:
        data = (
            obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, "model_dump")
            else obj_in.copy() if isinstance(obj_in, dict) else dict(obj_in)
        )
        return Scholarship(**data)


    async def publish(self, id: UUID) -> Scholarship:
        """
        Publish a scholarship (make it active).
        Raises BusinessRuleViolation if already published.
        """
        async with self.transaction_manager.transaction():
            scholarship = await self._require_entity(id)
            self._prevent_redundant_state(
                scholarship.is_active, True, f"Scholarship {id} is already published."
            )
            return await self.repository.update(id, {"is_active": True})  # type: ignore

    async def unpublish(self, id: UUID) -> Scholarship:
        """
        Unpublish a scholarship (make it inactive).
        Raises BusinessRuleViolation if already unpublished.
        """
        async with self.transaction_manager.transaction():
            scholarship = await self._require_entity(id)
            self._prevent_redundant_state(
                scholarship.is_active,
                False,
                f"Scholarship {id} is already unpublished.",
            )
            return await self.repository.update(id, {"is_active": False})  # type: ignore

    async def search(self, **kwargs: Any) -> Sequence[Scholarship]:
        """
        Search scholarships using arbitrary kwargs filters via repository.
        """
        return await self.repository.search(**kwargs)

    async def active_scholarships(
        self, pagination: PaginationParams
    ) -> PaginatedResult[Scholarship]:
        """
        Retrieve a paginated list of all active scholarships.
        """
        return await self.repository.get_active(pagination)

    async def create(self, obj_in: Any, user: Any = None) -> Scholarship:
        data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else dict(obj_in)

        # Validate deadline is not in the past
        import datetime
        from datetime import date
        deadline = data.get("deadline")
        if deadline:
            if isinstance(deadline, str):
                try:
                    deadline_val = datetime.datetime.fromisoformat(deadline).date()
                except ValueError:
                    deadline_val = datetime.datetime.strptime(deadline, "%Y-%m-%d").date()
            elif isinstance(deadline, datetime.datetime):
                deadline_val = deadline.date()
            elif isinstance(deadline, datetime.date):
                deadline_val = deadline
            else:
                deadline_val = deadline
                
            today = date.today()
            if deadline_val < today:
                from app.services.exceptions import BusinessRuleViolation
                raise BusinessRuleViolation("Scholarship deadline cannot be in the past")

        # Check duplicate scholarship title
        title = data.get("title")
        if title:
            existing_schs = await self.repository.list(title=title)
            if existing_schs:
                from app.services.exceptions import EntityAlreadyExists
                raise EntityAlreadyExists(f"Scholarship with title '{title}' already exists.")

        # Validate agency exists if user is provided
        if user is not None:
            from app.models.enums import UserRole
            if user.role not in [UserRole.AGENCY, UserRole.ADMIN]:
                from app.services.exceptions import PermissionDenied
                raise PermissionDenied("Only agency users can create scholarships.")

            if user.role == UserRole.AGENCY:
                from app.models.agency import Agency
                from sqlalchemy import select
                stmt = select(Agency).where(Agency.user_id == str(user.id))
                result = await self.repository.session.execute(stmt)
                agency = result.scalar_one_or_none()
                if not agency:
                    from app.services.exceptions import EntityNotFound
                    raise EntityNotFound(f"Agency profile for user {user.id} not found.")
                data["agency_id"] = str(agency.id)
        else:
            # Fallback for unit tests that pass dict directly
            agency_id = data.get("agency_id")
            if not agency_id:
                from app.services.exceptions import BusinessRuleViolation
                raise BusinessRuleViolation("Invalid agency")

        async with self.transaction_manager.transaction():
            model_instance = self._to_model(data)
            return await self.repository.create(model_instance)


    async def update(self, id: UUID, obj_in: Any, user: Any = None) -> Scholarship | None:
        if user is not None:
            from app.models.enums import UserRole
            if user.role not in [UserRole.AGENCY, UserRole.ADMIN]:
                from app.services.exceptions import PermissionDenied
                raise PermissionDenied("Only agency users can update scholarships.")

        data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else dict(obj_in)

        # Validate deadline is not in the past
        import datetime
        from datetime import date
        deadline = data.get("deadline")
        if deadline:
            if isinstance(deadline, str):
                try:
                    deadline_val = datetime.datetime.fromisoformat(deadline).date()
                except ValueError:
                    deadline_val = datetime.datetime.strptime(deadline, "%Y-%m-%d").date()
            elif isinstance(deadline, datetime.datetime):
                deadline_val = deadline.date()
            elif isinstance(deadline, datetime.date):
                deadline_val = deadline
            else:
                deadline_val = deadline
                
            today = date.today()
            if deadline_val < today:
                from app.services.exceptions import BusinessRuleViolation
                raise BusinessRuleViolation("Scholarship deadline cannot be in the past")

        # Validate title duplicate
        title = data.get("title")
        if title:
            existing_schs = await self.repository.list(title=title)
            if existing_schs and any(str(s.id) != str(id) for s in existing_schs):
                from app.services.exceptions import EntityAlreadyExists
                raise EntityAlreadyExists(f"Scholarship with title '{title}' already exists.")

        async with self.transaction_manager.transaction():
            await self._require_entity(id)
            return await self.repository.update(id, data)

    async def delete(self, id: UUID, user: Any = None) -> bool:
        if user is not None:
            from app.models.enums import UserRole
            if user.role not in [UserRole.AGENCY, UserRole.ADMIN]:
                from app.services.exceptions import PermissionDenied
                raise PermissionDenied("Only agency users can delete scholarships.")
        
        async with self.transaction_manager.transaction():
            await self._require_entity(id)
            return await self.repository.delete(id)

