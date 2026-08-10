from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agency import Agency
from app.models.enums import DegreeLevel, FundingType, LeadStatus, UserRole
from app.models.lead import Lead
from app.models.scholarship import Scholarship
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.repositories.agency_repository import AgencyRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.params import PaginationParams
from app.repositories.scholarship_repository import ScholarshipRepository
from app.repositories.student_profile_repository import StudentProfileRepository
from app.repositories.transaction import TransactionManager
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_domain_repositories_methods(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    student_repo = StudentProfileRepository(db_session)
    agency_repo = AgencyRepository(db_session)
    scholarship_repo = ScholarshipRepository(db_session)
    lead_repo = LeadRepository(db_session)

    uid = str(uuid4())
    user = User(
        id=uid, email=f"{uid}@test.com", password_hash="hash", role=UserRole.STUDENT
    )
    await user_repo.create(user)

    fetched_user = await user_repo.get_by_email(f"{uid}@test.com")
    assert fetched_user is not None
    assert fetched_user.id == uid

    profile = StudentProfile(
        id=str(uuid4()), user_id=uid, first_name="Test", last_name="Student"
    )
    await student_repo.create(profile)
    fetched_profile = await student_repo.get_by_user_id(uid)
    assert fetched_profile is not None
    assert fetched_profile.id == profile.id

    auid = str(uuid4())
    auser = User(
        id=auid, email=f"{auid}@agency.com", password_hash="hash", role=UserRole.AGENCY
    )
    await user_repo.create(auser)

    agency = Agency(id=str(uuid4()), user_id=auid, agency_name="Agency Test")
    await agency_repo.create(agency)
    fetched_agency = await agency_repo.get_by_user_id(auid)
    assert fetched_agency is not None
    assert fetched_agency.id == agency.id

    sid = str(uuid4())
    sch = Scholarship(
        id=sid,
        title="Sch 1",
        country="USA",
        degree_level=DegreeLevel.BACHELOR,
        funding_type=FundingType.FULLY_FUNDED,
        is_active=True,
    )
    await scholarship_repo.create(sch)

    sid2 = str(uuid4())
    sch2 = Scholarship(
        id=sid2,
        title="Sch 2",
        country="USA",
        degree_level=DegreeLevel.BACHELOR,
        funding_type=FundingType.FULLY_FUNDED,
        is_active=False,
    )
    await scholarship_repo.create(sch2)

    active_sch = await scholarship_repo.get_active(
        PaginationParams(page=1, page_size=10)
    )
    assert len(active_sch.items) >= 1
    assert any(s.id == sid for s in active_sch.items)
    assert not any(s.id == sid2 for s in active_sch.items)

    lid = str(uuid4())
    lead = Lead(
        id=lid,
        student_id=profile.id,
        agency_id=agency.id,
        scholarship_id=sid,
        status=LeadStatus.NEW,
    )
    await lead_repo.create(lead)

    leads_s = await lead_repo.get_by_student_id(profile.id)
    assert len(leads_s) == 1
    assert leads_s[0].id == lid

    leads_a = await lead_repo.get_by_agency_id(agency.id)
    assert len(leads_a) == 1

    leads_sch = await lead_repo.get_by_scholarship_id(sid)
    assert len(leads_sch) == 1


@pytest.mark.asyncio
async def test_cross_repository_transaction_commit(db_session: AsyncSession):
    tm = TransactionManager(db_session)
    user_repo = UserRepository(db_session)
    student_repo = StudentProfileRepository(db_session)
    sch_repo = ScholarshipRepository(db_session)
    lead_repo = LeadRepository(db_session)

    uid = str(uuid4())
    pid = str(uuid4())
    sid = str(uuid4())
    lid = str(uuid4())

    async with tm.transaction():
        user = User(id=uid, email=f"{uid}@commit.com", password_hash="hash")
        await user_repo.create(user)

        prof = StudentProfile(id=pid, user_id=uid, first_name="C", last_name="C")
        await student_repo.create(prof)

        sch = Scholarship(
            id=sid,
            title="C",
            country="USA",
            degree_level=DegreeLevel.BACHELOR,
            funding_type=FundingType.FULLY_FUNDED,
        )
        await sch_repo.create(sch)

        lead = Lead(id=lid, student_id=pid, scholarship_id=sid)
        await lead_repo.create(lead)

    fetched_lead = await lead_repo.get_by_id(UUID(lid))
    assert fetched_lead is not None
    assert fetched_lead.student_id == pid


@pytest.mark.asyncio
async def test_cross_repository_transaction_rollback(db_session: AsyncSession):
    tm = TransactionManager(db_session)
    user_repo = UserRepository(db_session)
    student_repo = StudentProfileRepository(db_session)

    uid = str(uuid4())
    pid = str(uuid4())

    try:
        async with tm.transaction():
            user = User(id=uid, email=f"{uid}@rollback.com", password_hash="hash")
            await user_repo.create(user)

            prof = StudentProfile(id=pid, user_id=uid, first_name="R", last_name="R")
            await student_repo.create(prof)

            raise ValueError("Force rollback")
    except ValueError:
        pass

    u = await user_repo.get_by_id(UUID(uid))
    assert u is None
    p = await student_repo.get_by_id(UUID(pid))
    assert p is None
