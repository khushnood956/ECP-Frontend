from collections.abc import Sequence
from typing import Any
from uuid import UUID

from app.models.scholarship import Scholarship
from app.repositories.params import PaginatedResult, PaginationParams
from app.repositories.scholarship_repository import ScholarshipRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService


class ScholarshipService(BaseService[Scholarship, Any, Any]):
    repository: ScholarshipRepository
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

    async def _get_user_agency_id(self, user: Any) -> str | None:
        if not user:
            return None
        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        if role_str != "agency":
            return None

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

    async def _check_read_visibility(self, scholarship: Scholarship, user: Any = None) -> None:
        from app.models.enums import UserRole
        from app.services.exceptions import PermissionDenied

        if user is None:
            raise PermissionDenied("You do not have permission to view this scholarship.")

        if user.role == UserRole.ADMIN:
            return

        if user.role == UserRole.AGENCY:
            agency_id = await self._get_user_agency_id(user)
            # Block access to other agencies' scholarships
            sch_agency_id = getattr(scholarship, "agency_id", None)
            if sch_agency_id is not None and (not agency_id or str(sch_agency_id) != str(agency_id)):
                raise PermissionDenied("You do not have permission to view this scholarship.")
            return

        # For student / other roles:
        if scholarship.is_active:
            return

        raise PermissionDenied("You do not have permission to view this scholarship.")


    async def get_by_id(self, id: UUID, user: Any = None) -> Scholarship | None:
        scholarship = await super().get_by_id(id)
        if scholarship:
            await self._check_read_visibility(scholarship, user)
        return scholarship

    async def list_scholarships(self, user: Any, pagination: PaginationParams) -> PaginatedResult[Scholarship]:
        own_agency_id = await self._get_user_agency_id(user)
        return await self.repository.list_scoped(pagination, user.role, own_agency_id)



    async def publish(self, id: UUID, user: Any = None) -> Scholarship:
        """
        Publish a scholarship (make it active).
        Raises BusinessRuleViolation if already published.
        """
        async with self.transaction_manager.transaction():
            scholarship = await self._require_entity(id)
            if user is not None:
                from app.models.enums import UserRole
                if user.role != UserRole.ADMIN:
                    if user.role != UserRole.AGENCY:
                        from app.services.exceptions import PermissionDenied
                        raise PermissionDenied("Only agency users can publish scholarships.")
                    from sqlalchemy import select

                    from app.models.agency import Agency
                    stmt = select(Agency).where(Agency.user_id == str(user.id))
                    result = await self.repository.session.execute(stmt)
                    agency = result.scalar_one_or_none()
                    if not agency or str(scholarship.agency_id) != str(agency.id):
                        from app.services.exceptions import PermissionDenied
                        raise PermissionDenied("You do not have permission to publish this scholarship.")
                        
            self._prevent_redundant_state(
                scholarship.is_active, True, f"Scholarship {id} is already published."
            )
            return await self.repository.update(id, {"is_active": True})  # type: ignore

    async def unpublish(self, id: UUID, user: Any = None) -> Scholarship:
        """
        Unpublish a scholarship (make it inactive).
        Raises BusinessRuleViolation if already unpublished.
        """
        async with self.transaction_manager.transaction():
            scholarship = await self._require_entity(id)
            if user is not None:
                from app.models.enums import UserRole
                if user.role != UserRole.ADMIN:
                    if user.role != UserRole.AGENCY:
                        from app.services.exceptions import PermissionDenied
                        raise PermissionDenied("Only agency users can unpublish scholarships.")
                    from sqlalchemy import select

                    from app.models.agency import Agency
                    stmt = select(Agency).where(Agency.user_id == str(user.id))
                    result = await self.repository.session.execute(stmt)
                    agency = result.scalar_one_or_none()
                    if not agency or str(scholarship.agency_id) != str(agency.id):
                        from app.services.exceptions import PermissionDenied
                        raise PermissionDenied("You do not have permission to unpublish this scholarship.")
                        
            self._prevent_redundant_state(
                scholarship.is_active,
                False,
                f"Scholarship {id} is already unpublished.",
            )
            return await self.repository.update(id, {"is_active": False})  # type: ignore

    async def search(self, user: Any, **kwargs: Any) -> Sequence[Scholarship]:
        """
        Search scholarships using arbitrary kwargs filters via repository.
        """
        own_agency_id = await self._get_user_agency_id(user)
        return await self.repository.search_scoped(user.role, own_agency_id, **kwargs)

    async def list_active_scoped(self, user: Any) -> Sequence[Scholarship]:
        """
        Retrieve a list of all active scholarships scoped by user role.
        """
        own_agency_id = await self._get_user_agency_id(user)
        return await self.repository.list_active_scoped(user.role, own_agency_id)

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
        deadline = data.get("deadline")
        if deadline:
            if isinstance(deadline, str):
                try:
                    deadline_val = datetime.datetime.fromisoformat(deadline).date()
                except ValueError:
                    deadline_val = datetime.datetime.strptime(deadline, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).date()
            elif isinstance(deadline, datetime.datetime):
                deadline_val = deadline.date()
            elif isinstance(deadline, datetime.date):
                deadline_val = deadline
            else:
                deadline_val = deadline
                
            today = datetime.datetime.now(datetime.timezone.utc).date()
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
                from sqlalchemy import select

                from app.models.agency import Agency
                stmt = select(Agency).where(Agency.user_id == str(user.id))
                result = await self.repository.session.execute(stmt)
                agency = result.scalar_one_or_none()
                if not agency:
                    from app.services.exceptions import EntityNotFound
                    raise EntityNotFound(f"Agency profile for user {user.id} not found.")
                data["agency_id"] = str(agency.id)
            elif user.role == UserRole.ADMIN:
                target_agency_id = data.get("agency_id")
                if target_agency_id:
                    from sqlalchemy import select

                    from app.models.agency import Agency
                    stmt = select(Agency).where(Agency.id == str(target_agency_id))
                    result = await self.repository.session.execute(stmt)
                    agency = result.scalar_one_or_none()
                    if not agency:
                        from app.services.exceptions import EntityNotFound
                        raise EntityNotFound(f"Agency with ID {target_agency_id} not found.")
                    data["agency_id"] = str(target_agency_id)
                else:
                    from app.services.exceptions import BusinessRuleViolation
                    raise BusinessRuleViolation("Admin must specify agency_id when creating a scholarship.")
        else:
            # Fallback for unit tests that pass dict directly
            agency_id = data.get("agency_id")
            if not agency_id:
                from app.services.exceptions import BusinessRuleViolation
                raise BusinessRuleViolation("Invalid agency")

        async with self.transaction_manager.transaction():
            app_reqs = data.pop("application_requirements", None)
            model_instance = self._to_model(data)
            created = await self.repository.create(model_instance)
            
            if app_reqs:
                import uuid
                from app.models.application import ScholarshipApplicationRequirement
                for req in app_reqs:
                    if hasattr(req, "model_dump"):
                        req = req.model_dump()
                    elif not isinstance(req, dict):
                        req = dict(req)
                    db_req = ScholarshipApplicationRequirement(
                        id=str(uuid.uuid4()),
                        scholarship_id=created.id,
                        field_key=req.get("field_key"),
                        label=req.get("label"),
                        field_type=req.get("field_type"),
                        is_required=req.get("is_required", True),
                        options=req.get("options"),
                        display_order=req.get("display_order", 0)
                    )
                    self.transaction_manager.session.add(db_req)

                await self.transaction_manager.session.flush()

            reloaded = await self.repository.get_by_id(created.id)
            return reloaded or created


    async def update(self, id: UUID, obj_in: Any, user: Any = None) -> Scholarship | None:
        async with self.transaction_manager.transaction():
            scholarship = await self._require_entity(id)
            if user is not None:
                from app.models.enums import UserRole
                if user.role not in [UserRole.AGENCY, UserRole.ADMIN]:
                    from app.services.exceptions import PermissionDenied
                    raise PermissionDenied("Only agency users can update scholarships.")
                
                if user.role == UserRole.AGENCY:
                    from sqlalchemy import select

                    from app.models.agency import Agency
                    stmt = select(Agency).where(Agency.user_id == str(user.id))
                    result = await self.repository.session.execute(stmt)
                    agency = result.scalar_one_or_none()
                    if not agency or str(scholarship.agency_id) != str(agency.id):
                        from app.services.exceptions import PermissionDenied
                        raise PermissionDenied("You do not have permission to update this scholarship.")

            data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else dict(obj_in)

            # Prevent mass assignment of sensitive lifecycle and ownership fields
            data.pop("is_active", None)
            data.pop("agency_id", None)
            data.pop("id", None)

            # Validate deadline is not in the past
            import datetime
            deadline = data.get("deadline")
            if deadline:
                if isinstance(deadline, str):
                    try:
                        deadline_val = datetime.datetime.fromisoformat(deadline).date()
                    except ValueError:
                        deadline_val = datetime.datetime.strptime(deadline, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).date()
                elif isinstance(deadline, datetime.datetime):
                    deadline_val = deadline.date()
                elif isinstance(deadline, datetime.date):
                    deadline_val = deadline
                else:
                    deadline_val = deadline
                    
                today = datetime.datetime.now(datetime.timezone.utc).date()
                if deadline_val < today:
                    from app.services.exceptions import BusinessRuleViolation
                    raise BusinessRuleViolation("Scholarship deadline cannot be in the past")

            app_reqs = data.pop("application_requirements", None)
            title = data.get("title")
            if title:
                existing_schs = await self.repository.list(title=title)
                if existing_schs and any(str(s.id) != str(id) for s in existing_schs):
                    from app.services.exceptions import EntityAlreadyExists
                    raise EntityAlreadyExists(f"Scholarship with title '{title}' already exists.")

            updated = await self.repository.update(id, data)
            
            if app_reqs is not None:
                from sqlalchemy import delete
                from app.models.application import ScholarshipApplicationRequirement
                import uuid
                
                del_stmt = delete(ScholarshipApplicationRequirement).where(ScholarshipApplicationRequirement.scholarship_id == str(id))
                await self.transaction_manager.session.execute(del_stmt)
                
                for req in app_reqs:
                    if hasattr(req, "model_dump"):
                        req = req.model_dump()
                    elif not isinstance(req, dict):
                        req = dict(req)
                    db_req = ScholarshipApplicationRequirement(
                        id=str(uuid.uuid4()),
                        scholarship_id=str(id),
                        field_key=req.get("field_key"),
                        label=req.get("label"),
                        field_type=req.get("field_type"),
                        is_required=req.get("is_required", True),
                        options=req.get("options"),
                        display_order=req.get("display_order", 0)
                    )
                    self.transaction_manager.session.add(db_req)

                await self.transaction_manager.session.flush()

        await self.transaction_manager.session.flush()

        reloaded = await self.repository.get_by_id(id)
        return reloaded or updated

    async def delete(self, id: UUID, user: Any = None) -> bool:
        async with self.transaction_manager.transaction():
            scholarship = await self._require_entity(id)
            
            if user is not None:
                from app.models.enums import UserRole
                if user.role not in [UserRole.AGENCY, UserRole.ADMIN]:
                    from app.services.exceptions import PermissionDenied
                    raise PermissionDenied("Only agency users can delete scholarships.")
                    
                if user.role == UserRole.AGENCY:
                    from sqlalchemy import select

                    from app.models.agency import Agency
                    stmt = select(Agency).where(Agency.user_id == str(user.id))
                    result = await self.repository.session.execute(stmt)
                    agency = result.scalar_one_or_none()
                    if not agency or str(scholarship.agency_id) != str(agency.id):
                        from app.services.exceptions import PermissionDenied
                        raise PermissionDenied("You do not have permission to delete this scholarship.")
            
            return await self.repository.delete(id)

