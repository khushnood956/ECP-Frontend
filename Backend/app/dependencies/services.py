from fastapi import Depends

from app.dependencies.database import get_transaction_manager
from app.dependencies.repositories import (
    get_agency_repository,
    get_lead_repository,
    get_scholarship_repository,
    get_student_repository,
    get_user_repository,
)
from app.repositories.agency_repository import AgencyRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.scholarship_repository import ScholarshipRepository
from app.repositories.student_profile_repository import StudentProfileRepository
from app.repositories.transaction import TransactionManager
from app.repositories.user_repository import UserRepository
from app.services.agency_service import AgencyService
from app.services.lead_service import LeadService
from app.services.scholarship_service import ScholarshipService
from app.services.student_service import StudentService
from app.services.user_service import UserService


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
) -> UserService:
    """Provides a fully initialized UserService."""
    return UserService(repository=repository, transaction_manager=transaction_manager)


def get_student_service(
    repository: StudentProfileRepository = Depends(get_student_repository),
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
) -> StudentService:
    """Provides a fully initialized StudentService."""
    return StudentService(
        repository=repository, transaction_manager=transaction_manager
    )


def get_agency_service(
    repository: AgencyRepository = Depends(get_agency_repository),
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
) -> AgencyService:
    """Provides a fully initialized AgencyService."""
    return AgencyService(repository=repository, transaction_manager=transaction_manager)


def get_scholarship_service(
    repository: ScholarshipRepository = Depends(get_scholarship_repository),
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
) -> ScholarshipService:
    """Provides a fully initialized ScholarshipService."""
    return ScholarshipService(
        repository=repository, transaction_manager=transaction_manager
    )


def get_lead_service(
    repository: LeadRepository = Depends(get_lead_repository),
    agency_repository: AgencyRepository = Depends(get_agency_repository),
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
) -> LeadService:
    """Provides a fully initialized LeadService with its multiple repository dependencies."""
    return LeadService(
        repository=repository,
        agency_repository=agency_repository,
        transaction_manager=transaction_manager,
    )

from app.services.auth_service import AuthService


async def get_auth_service(user_service=Depends(get_user_service)) -> AuthService:
    return AuthService(user_service=user_service)
