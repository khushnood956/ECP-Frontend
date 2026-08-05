from typing import Any, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.models.agency import Agency
from app.models.enums import AgencyVerificationStatus
from app.repositories.agency_repository import AgencyRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService
from app.services.exceptions import BusinessRuleViolation


class AgencyService(BaseService[Agency, Any, Any]):
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

    def __init__(self, repository: AgencyRepository, transaction_manager: TransactionManager):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    async def get_by_registration_number(self, registration_number: str) -> Optional[Agency]:
        """
        Retrieve an agency by its registration number.
        """
        return await self.repository.get_by_registration_number(registration_number)

    async def verify_agency(self, id: UUID) -> Agency:
        """
        Verify an agency.
        Raises BusinessRuleViolation if already verified.
        """
        async with self.transaction_manager.transaction():
            agency = await self._require_entity(id)
            self._prevent_redundant_state(agency.verification_status, AgencyVerificationStatus.VERIFIED, f"Agency {id} is already verified.")
            
            update_data = {
                "verification_status": AgencyVerificationStatus.VERIFIED,
                "verified_at": datetime.now(timezone.utc)
            }
            return await self.repository.update(id, update_data)  # type: ignore

    async def suspend_agency(self, id: UUID) -> Agency:
        """
        Suspend an agency by marking its verification status as rejected.
        Raises BusinessRuleViolation if already suspended/rejected.
        """
        async with self.transaction_manager.transaction():
            agency = await self._require_entity(id)
            self._prevent_redundant_state(agency.verification_status, AgencyVerificationStatus.REJECTED, f"Agency {id} is already suspended.")
            
            update_data = {
                "verification_status": AgencyVerificationStatus.REJECTED
            }
            return await self.repository.update(id, update_data)  # type: ignore
