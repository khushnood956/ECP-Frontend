from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db_session
from app.repositories.agency_repository import AgencyRepository
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.scholarship_repository import ScholarshipRepository
from app.repositories.student_profile_repository import StudentProfileRepository
from app.repositories.user_repository import UserRepository


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    """Provides a fresh UserRepository bound to the current session."""
    return UserRepository(session)


def get_student_repository(
    session: AsyncSession = Depends(get_db_session),
) -> StudentProfileRepository:
    """Provides a fresh StudentProfileRepository bound to the current session."""
    return StudentProfileRepository(session)


def get_agency_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AgencyRepository:
    """Provides a fresh AgencyRepository bound to the current session."""
    return AgencyRepository(session)


def get_scholarship_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ScholarshipRepository:
    """Provides a fresh ScholarshipRepository bound to the current session."""
    return ScholarshipRepository(session)


def get_lead_repository(
    session: AsyncSession = Depends(get_db_session),
) -> LeadRepository:
    """Provides a fresh LeadRepository bound to the current session."""
    return LeadRepository(session)


def get_class_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ClassRepository:
    """Provides a fresh ClassRepository bound to the current session."""
    return ClassRepository(session)


def get_enrollment_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EnrollmentRepository:
    """Provides a fresh EnrollmentRepository bound to the current session."""
    return EnrollmentRepository(session)


def get_attendance_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AttendanceRepository:
    """Provides a fresh AttendanceRepository bound to the current session."""
    return AttendanceRepository(session)


from app.repositories.university_repository import UniversityRepository

def get_university_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UniversityRepository:
    """Provides a fresh UniversityRepository bound to the current session."""
    return UniversityRepository(session)

