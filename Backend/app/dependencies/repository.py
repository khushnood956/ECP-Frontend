from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.transaction import TransactionManager
from app.repositories.user_repository import UserRepository
from app.repositories.student_profile_repository import StudentProfileRepository
from app.repositories.agency_repository import AgencyRepository
from app.repositories.scholarship_repository import ScholarshipRepository
from app.repositories.lead_repository import LeadRepository

def get_transaction_manager(session: AsyncSession = Depends(get_db)) -> TransactionManager:
    return TransactionManager(session)

def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)

def get_student_profile_repository(session: AsyncSession = Depends(get_db)) -> StudentProfileRepository:
    return StudentProfileRepository(session)

def get_agency_repository(session: AsyncSession = Depends(get_db)) -> AgencyRepository:
    return AgencyRepository(session)

def get_scholarship_repository(session: AsyncSession = Depends(get_db)) -> ScholarshipRepository:
    return ScholarshipRepository(session)

def get_lead_repository(session: AsyncSession = Depends(get_db)) -> LeadRepository:
    return LeadRepository(session)
