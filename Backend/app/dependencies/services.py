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

def get_admin_service(
    user_repo: UserRepository = Depends(get_user_repository),
    student_repo: StudentProfileRepository = Depends(get_student_repository),
    agency_repo: AgencyRepository = Depends(get_agency_repository),
    scholarship_repo: ScholarshipRepository = Depends(get_scholarship_repository),
    lead_repo: LeadRepository = Depends(get_lead_repository)
):
    from app.services.admin_service import AdminService
    return AdminService(
        user_repo=user_repo,
        student_repo=student_repo,
        agency_repo=agency_repo,
        scholarship_repo=scholarship_repo,
        lead_repo=lead_repo
    )

from app.dependencies.repositories import (
    get_attendance_repository,
    get_class_repository,
    get_enrollment_repository,
)
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.services.attendance_service import AttendanceService
from app.services.class_service import ClassService
from app.services.enrollment_service import EnrollmentService


def get_class_service(
    repository: ClassRepository = Depends(get_class_repository),
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
) -> ClassService:
    return ClassService(repository=repository, transaction_manager=transaction_manager)


def get_enrollment_service(
    repository: EnrollmentRepository = Depends(get_enrollment_repository),
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
) -> EnrollmentService:
    return EnrollmentService(repository=repository, transaction_manager=transaction_manager)


def get_attendance_service(
    repository: AttendanceRepository = Depends(get_attendance_repository),
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
) -> AttendanceService:
    return AttendanceService(repository=repository, transaction_manager=transaction_manager)


from app.dependencies.repositories import get_university_repository
from app.repositories.university_repository import UniversityRepository
from app.services.university_service import UniversityService

def get_university_service(
    repository: UniversityRepository = Depends(get_university_repository),
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
) -> UniversityService:
    """Provides a fully initialized UniversityService."""
    return UniversityService(repository=repository, transaction_manager=transaction_manager)

