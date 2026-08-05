from typing import Any, Sequence
from uuid import UUID

from app.models.scholarship import Scholarship
from app.repositories.scholarship_repository import ScholarshipRepository
from app.repositories.transaction import TransactionManager
from app.repositories.params import PaginationParams, PaginatedResult
from app.services.base import BaseService
from app.services.exceptions import BusinessRuleViolation


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

    def __init__(self, repository: ScholarshipRepository, transaction_manager: TransactionManager):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    async def publish(self, id: UUID) -> Scholarship:
        """
        Publish a scholarship (make it active).
        Raises BusinessRuleViolation if already published.
        """
        async with self.transaction_manager.transaction():
            scholarship = await self._require_entity(id)
            self._prevent_redundant_state(scholarship.is_active, True, f"Scholarship {id} is already published.")
            return await self.repository.update(id, {"is_active": True})  # type: ignore

    async def unpublish(self, id: UUID) -> Scholarship:
        """
        Unpublish a scholarship (make it inactive).
        Raises BusinessRuleViolation if already unpublished.
        """
        async with self.transaction_manager.transaction():
            scholarship = await self._require_entity(id)
            self._prevent_redundant_state(scholarship.is_active, False, f"Scholarship {id} is already unpublished.")
            return await self.repository.update(id, {"is_active": False})  # type: ignore

    async def search(self, **kwargs: Any) -> Sequence[Scholarship]:
        """
        Search scholarships using arbitrary kwargs filters via repository.
        """
        return await self.repository.search(**kwargs)

    async def active_scholarships(self, pagination: PaginationParams) -> PaginatedResult[Scholarship]:
        """
        Retrieve a paginated list of all active scholarships.
        """
        return await self.repository.get_active(pagination)
