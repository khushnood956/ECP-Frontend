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
from app.services.exceptions import BusinessRuleViolation, EntityNotFound


class LeadService(BaseService[Lead, Any, Any]):
    """
    Business Responsibility:
    Handles lead assignments, status transitions, and follow-ups.

    Does:
    - Assign leads to agencies and update lead statuses.
    - Schedule follow-up dates enforcing business time rules.
    - Query leads associated with specific students.

    Does Not:
    - Delete leads directly (typically managed by soft deletes or administrative services).

    Dependencies:
    - LeadRepository for primary lead data access.
    - AgencyRepository for cross-repository agency existence checks.

    Transaction Behaviour:
    - Read operations (leads_by_student) do not use transactions.
    - Mutating operations (assign_agency, update_status, schedule_follow_up) are enclosed within TransactionManager.
    """

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
            else obj_in
        )
        return Lead(**data)

    async def assign_agency(self, lead_id: UUID, agency_id: UUID) -> Lead:
        """
        Assign an agency to a lead.
        Raises EntityNotFound if the target agency does not exist.
        """
        async with self.transaction_manager.transaction():
            lead = await self._require_entity(lead_id)

            # Cross-repository validation
            agency = await self.agency_repository.get_by_id(agency_id)
            if not agency:
                raise EntityNotFound(f"Agency {agency_id} does not exist.")

            return await self.repository.update(lead_id, {"agency_id": str(agency_id)})  # type: ignore

    async def update_status(self, lead_id: UUID, new_status: LeadStatus) -> Lead:
        """
        Update the status of a lead.
        Raises BusinessRuleViolation if lead is already in this status.
        """
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
        """
        Schedule a follow-up date for a lead.
        Raises BusinessRuleViolation if the date is in the past.
        """
        if follow_up_date.tzinfo is None:
            # Localize naive datetimes to UTC for comparison
            follow_up_date = follow_up_date.replace(tzinfo=timezone.utc)

        if follow_up_date < datetime.now(timezone.utc):
            raise BusinessRuleViolation("Cannot schedule follow-up in the past.")

        async with self.transaction_manager.transaction():
            await self._require_entity(lead_id)
            return await self.repository.update(lead_id, {"follow_up_date": follow_up_date})  # type: ignore

    async def leads_by_student(self, student_id: UUID | str) -> Sequence[Lead]:
        """
        Retrieve all leads associated with a specific student.
        """
        return await self.repository.get_by_student_id(student_id)
