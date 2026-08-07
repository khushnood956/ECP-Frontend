from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.models.enums import LeadStatus
from app.models.lead import Lead
from app.repositories.agency_repository import AgencyRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService
from app.services.exceptions import BusinessRuleViolation, EntityNotFound, PermissionDenied, EntityAlreadyExists


class LeadService(BaseService[Lead, Any, Any]):
    def __init__(
        self,
        repository: LeadRepository,
        agency_repository: AgencyRepository,
        transaction_manager: TransactionManager,
    ):
        super().__init__(repository=repository, transaction_manager=transaction_manager)
        self.agency_repository = agency_repository

    def _to_model(self, obj_in: Any) -> Lead:
        data = (
            obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, "model_dump")
            else dict(obj_in)
        )
        return Lead(**data)

    async def assign_agency(self, lead_id: UUID, agency_id: UUID) -> Lead:
        async with self.transaction_manager.transaction():
            lead = await self._require_entity(lead_id)
            agency = await self.agency_repository.get_by_id(agency_id)
            if not agency:
                raise EntityNotFound(f"Agency {agency_id} does not exist.")
            return await self.repository.update(lead_id, {"agency_id": str(agency_id)})  # type: ignore

    async def update_status(self, lead_id: UUID, new_status: LeadStatus) -> Lead:
        async with self.transaction_manager.transaction():
            lead = await self._require_entity(lead_id)
            self._prevent_redundant_state(
                lead.status,
                new_status,
                f"Lead is already in status '{new_status.value}'.",
            )
            update_data = {
                "status": new_status,
                "status_updated_at": datetime.now(timezone.utc),
            }
            return await self.repository.update(lead_id, update_data)  # type: ignore

    async def schedule_follow_up(self, lead_id: UUID, follow_up_date: datetime) -> Lead:
        if follow_up_date.tzinfo is None:
            follow_up_date = follow_up_date.replace(tzinfo=timezone.utc)

        if follow_up_date < datetime.now(timezone.utc):
            raise BusinessRuleViolation("Cannot schedule follow-up in the past.")

        async with self.transaction_manager.transaction():
            await self._require_entity(lead_id)
            return await self.repository.update(lead_id, {"follow_up_date": follow_up_date})  # type: ignore

    async def leads_by_student(self, student_id: UUID | str) -> Sequence[Lead]:
        return await self.repository.get_by_student_id(student_id)

    async def get_by_id(self, id: UUID, user: Any = None) -> Lead | None:
        lead = await self.repository.get_by_id(id)
        if not lead:
            return None

        if user is not None:
            from app.models.enums import UserRole
            if user.role == UserRole.STUDENT:
                from app.models.student_profile import StudentProfile
                from sqlalchemy import select
                stmt = select(StudentProfile).where(StudentProfile.user_id == str(user.id))
                result = await self.repository.session.execute(stmt)
                student_profile = result.scalar_one_or_none()
                if not student_profile or str(lead.student_id) != str(student_profile.id):
                    raise PermissionDenied("You do not have permission to view this lead.")
            elif user.role == UserRole.AGENCY:
                from app.models.agency import Agency
                from app.models.scholarship import Scholarship
                from sqlalchemy import select
                stmt = select(Agency).where(Agency.user_id == str(user.id))
                result = await self.repository.session.execute(stmt)
                agency = result.scalar_one_or_none()
                
                stmt_sch = select(Scholarship).where(Scholarship.id == str(lead.scholarship_id))
                res_sch = await self.repository.session.execute(stmt_sch)
                scholarship = res_sch.scalar_one_or_none()
                
                if not agency or not scholarship or str(scholarship.agency_id) != str(agency.id):
                    raise PermissionDenied("You do not have permission to view this lead.")
        return lead

    async def list_leads(self, user: Any, pagination: Any) -> Any:
        from app.models.enums import UserRole
        from app.repositories.params import FilterCondition, FilterOperator
        filters = []

        if user.role == UserRole.STUDENT:
            from app.models.student_profile import StudentProfile
            from sqlalchemy import select
            stmt = select(StudentProfile).where(StudentProfile.user_id == str(user.id))
            result = await self.repository.session.execute(stmt)
            student_profile = result.scalar_one_or_none()
            if not student_profile:
                from app.repositories.params import PaginatedResult
                return PaginatedResult(items=[], total=0, page=pagination.page, page_size=pagination.page_size, total_pages=0)
            filters.append(FilterCondition(field="student_id", operator=FilterOperator.EQ, value=str(student_profile.id)))

        elif user.role == UserRole.AGENCY:
            from app.models.agency import Agency
            from app.models.scholarship import Scholarship
            from sqlalchemy import select
            stmt = select(Agency).where(Agency.user_id == str(user.id))
            result = await self.repository.session.execute(stmt)
            agency = result.scalar_one_or_none()
            if not agency:
                from app.repositories.params import PaginatedResult
                return PaginatedResult(items=[], total=0, page=pagination.page, page_size=pagination.page_size, total_pages=0)
            
            stmt_sch = select(Scholarship.id).where(Scholarship.agency_id == str(agency.id))
            res_sch = await self.repository.session.execute(stmt_sch)
            sch_ids = [str(r) for r in res_sch.scalars().all()]
            
            if not sch_ids:
                from app.repositories.params import PaginatedResult
                return PaginatedResult(items=[], total=0, page=pagination.page, page_size=pagination.page_size, total_pages=0)
            
            filters.append(FilterCondition(field="scholarship_id", operator=FilterOperator.IN, value=sch_ids))

        return await self.repository.list_paginated(pagination=pagination, filters=filters)

    async def create(self, obj_in: Any, user: Any = None) -> Lead:
        if user is None:
            # Fallback for old tests
            async with self.transaction_manager.transaction():
                data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in
                student_id = data.get("student_id")
                scholarship_id = data.get("scholarship_id")
                existing = await self.repository.list(student_id=student_id, scholarship_id=scholarship_id)
                if existing:
                    raise BusinessRuleViolation("Lead already exists for this student and scholarship")
                model_instance = self._to_model(obj_in)
                return await self.repository.create(model_instance)

        from app.models.enums import UserRole
        if user.role != UserRole.STUDENT:
            raise PermissionDenied("Only student users can apply for scholarships.")

        from app.models.student_profile import StudentProfile
        from sqlalchemy import select
        stmt = select(StudentProfile).where(StudentProfile.user_id == str(user.id))
        result = await self.repository.session.execute(stmt)
        student_profile = result.scalar_one_or_none()
        if not student_profile:
            raise PermissionDenied("Student profile does not exist. Please create a student profile first.")

        data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else dict(obj_in)
        scholarship_id = data.get("scholarship_id")

        from app.models.scholarship import Scholarship
        stmt_sch = select(Scholarship).where(Scholarship.id == str(scholarship_id))
        res_sch = await self.repository.session.execute(stmt_sch)
        scholarship = res_sch.scalar_one_or_none()
        if not scholarship:
            raise EntityNotFound(f"Scholarship with id {scholarship_id} not found.")

        if not scholarship.is_active:
            raise BusinessRuleViolation("Scholarship is inactive.")

        if scholarship.deadline:
            from datetime import date
            if scholarship.deadline < date.today():
                raise BusinessRuleViolation("Scholarship deadline has passed.")

        # Duplicate detection
        existing = await self.repository.list(student_id=str(student_profile.id), scholarship_id=str(scholarship_id))
        if existing:
            raise EntityAlreadyExists("You have already applied for this scholarship.")

        # Serialize notes/motivation letter
        from app.schemas.lead import serialize_notes_field
        notes_str = serialize_notes_field(
            motivation_letter=data.get("motivation_letter"),
            documents=data.get("documents"),
            notes=data.get("notes")
        )

        db_data = {
            "student_id": str(student_profile.id),
            "scholarship_id": str(scholarship_id),
            "agency_id": str(scholarship.agency_id) if scholarship.agency_id else None,
            "status": LeadStatus.NEW,
            "notes": notes_str
        }

        async with self.transaction_manager.transaction():
            model_instance = self._to_model(db_data)
            return await self.repository.create(model_instance)

    async def update(self, id: UUID, obj_in: Any, user: Any = None) -> Lead | None:
        if user is None:
            # Fallback for old code/tests
            async with self.transaction_manager.transaction():
                await self._require_entity(id)
                data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else dict(obj_in)
                return await self.repository.update(id, data)

        from app.models.enums import UserRole
        lead = await self._require_entity(id)

        status_map = {
            LeadStatus.NEW: "submitted",
            LeadStatus.CONTACTED: "under_review",
            LeadStatus.IN_PROGRESS: "under_review",
            LeadStatus.WON: "accepted",
            LeadStatus.LOST: "rejected"
        }
        current_status_str = status_map.get(lead.status, "submitted")

        data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else dict(obj_in)

        if user.role == UserRole.STUDENT:
            if "status" in data and data["status"] is not None:
                raise PermissionDenied("Students are not allowed to update the status field.")

            from app.models.student_profile import StudentProfile
            from sqlalchemy import select
            stmt = select(StudentProfile).where(StudentProfile.user_id == str(user.id))
            result = await self.repository.session.execute(stmt)
            student_profile = result.scalar_one_or_none()
            if not student_profile or str(lead.student_id) != str(student_profile.id):
                raise PermissionDenied("You do not have permission to modify this lead.")

            if current_status_str != "submitted":
                raise BusinessRuleViolation("Cannot update application after it is reviewed.")

            from app.schemas.lead import parse_notes_field, serialize_notes_field
            ex_mot, ex_docs, ex_notes = parse_notes_field(lead.notes)

            new_mot = data.get("motivation_letter", ex_mot)
            new_docs = data.get("documents", ex_docs)
            new_notes = data.get("notes", ex_notes)

            notes_str = serialize_notes_field(new_mot, new_docs, new_notes)

            async with self.transaction_manager.transaction():
                return await self.repository.update(id, {"notes": notes_str})

        elif user.role == UserRole.AGENCY:
            for field in ["motivation_letter", "documents", "notes"]:
                if field in data and data[field] is not None:
                    raise PermissionDenied("Agencies are not allowed to update student-owned fields.")

            from app.models.agency import Agency
            from app.models.scholarship import Scholarship
            from sqlalchemy import select
            stmt = select(Agency).where(Agency.user_id == str(user.id))
            result = await self.repository.session.execute(stmt)
            agency = result.scalar_one_or_none()

            stmt_sch = select(Scholarship).where(Scholarship.id == str(lead.scholarship_id))
            res_sch = await self.repository.session.execute(stmt_sch)
            scholarship = res_sch.scalar_one_or_none()

            if not agency or not scholarship or str(scholarship.agency_id) != str(agency.id):
                raise PermissionDenied("You do not have permission to view or modify this lead.")

            target_status_str = data.get("status")
            if not target_status_str:
                raise BusinessRuleViolation("Status field is required.")

            if isinstance(target_status_str, LeadStatus):
                status_rev_map = {
                    LeadStatus.NEW: "submitted",
                    LeadStatus.CONTACTED: "under_review",
                    LeadStatus.IN_PROGRESS: "under_review",
                    LeadStatus.WON: "accepted",
                    LeadStatus.LOST: "rejected"
                }
                target_status_str = status_rev_map.get(target_status_str)

            allowed = False
            if current_status_str == "submitted":
                if target_status_str == "under_review":
                    allowed = True
                    target_status = LeadStatus.CONTACTED
            elif current_status_str == "under_review":
                if target_status_str == "accepted":
                    allowed = True
                    target_status = LeadStatus.WON
                elif target_status_str == "rejected":
                    allowed = True
                    target_status = LeadStatus.LOST
                elif target_status_str == "under_review":
                    allowed = True
                    target_status = LeadStatus.CONTACTED

            if not allowed:
                raise BusinessRuleViolation(f"Invalid status transition from '{current_status_str}' to '{target_status_str}'.")

            async with self.transaction_manager.transaction():
                return await self.repository.update(id, {"status": target_status, "status_updated_at": datetime.now(timezone.utc)})

        elif user.role == UserRole.ADMIN:
            update_fields = {}
            if "status" in data and data["status"] is not None:
                status_str = data["status"]
                status_map_rev = {
                    "submitted": LeadStatus.NEW,
                    "under_review": LeadStatus.CONTACTED,
                    "accepted": LeadStatus.WON,
                    "rejected": LeadStatus.LOST
                }
                if status_str in status_map_rev:
                    update_fields["status"] = status_map_rev[status_str]
                    update_fields["status_updated_at"] = datetime.now(timezone.utc)
            
            from app.schemas.lead import parse_notes_field, serialize_notes_field
            ex_mot, ex_docs, ex_notes = parse_notes_field(lead.notes)
            new_mot = data.get("motivation_letter", ex_mot)
            new_docs = data.get("documents", ex_docs)
            new_notes = data.get("notes", ex_notes)
            update_fields["notes"] = serialize_notes_field(new_mot, new_docs, new_notes)

            async with self.transaction_manager.transaction():
                return await self.repository.update(id, update_fields)
        else:
            raise PermissionDenied("Unauthorized role update request.")

    async def delete(self, id: UUID, user: Any = None) -> bool:
        if user is None:
            async with self.transaction_manager.transaction():
                await self._require_entity(id)
                return await self.repository.delete(id)

        from app.models.enums import UserRole
        lead = await self._require_entity(id)

        if user.role == UserRole.STUDENT:
            from app.models.student_profile import StudentProfile
            from sqlalchemy import select
            stmt = select(StudentProfile).where(StudentProfile.user_id == str(user.id))
            result = await self.repository.session.execute(stmt)
            student_profile = result.scalar_one_or_none()
            if not student_profile or str(lead.student_id) != str(student_profile.id):
                raise PermissionDenied("You do not have permission to withdraw this lead.")

            if lead.status != LeadStatus.NEW:
                raise BusinessRuleViolation("Cannot withdraw application after it has been reviewed.")

            async with self.transaction_manager.transaction():
                return await self.repository.delete(id)

        elif user.role == UserRole.AGENCY:
            raise PermissionDenied("Agencies are not allowed to delete applications.")

        elif user.role == UserRole.ADMIN:
            async with self.transaction_manager.transaction():
                return await self.repository.delete(id)
        else:
            raise PermissionDenied("Unauthorized role delete request.")
