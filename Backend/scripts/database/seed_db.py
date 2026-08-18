import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

# Add parent directories to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete

from app.core.security import get_password_hash
from app.db.database import AsyncSessionLocal
from app.models.agency import Agency
from app.models.enums import (
    AgencyVerificationStatus,
    DegreeLevel,
    FundingType,
    Gender,
    LeadStatus,
    UserRole,
)
from app.models.lead import Lead
from app.models.scholarship import Scholarship
from app.models.student_profile import StudentProfile
from app.models.university import University
from app.models.user import User


async def seed_database():
    print("Clearing existing database tables...")
    async with AsyncSessionLocal() as session:
        try:
            # 0. Delete existing records in dependency order
            await session.execute(delete(Lead))
            await session.execute(delete(Scholarship))
            await session.execute(delete(StudentProfile))
            await session.execute(delete(Agency))
            await session.execute(delete(User))
            await session.execute(delete(University))
            await session.commit()
            print("Database cleared successfully.")
        except Exception as e:
            await session.rollback()
            print(f"Failed to clear database: {e}")
            return

    print("Seeding database with realistic development data...")
    async with AsyncSessionLocal() as session:
        try:
            password_hash = get_password_hash("password123")
            
            # 1. Create Admin
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@test.com",
                password_hash=password_hash,
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
            )
            session.add(admin_user)
            print("Created Admin: admin@test.com")

            # 2. Create Student Users & Profiles
            # Student 1: Default Student (Alice)
            student1_id = str(uuid.uuid4())
            student1_user = User(
                id=student1_id,
                email="student@test.com",
                password_hash=password_hash,
                role=UserRole.STUDENT,
                is_active=True,
                is_verified=True,
            )
            student1_profile = StudentProfile(
                id=str(uuid.uuid4()),
                user_id=student1_id,
                first_name="Alice",
                last_name="Smith",
                gender=Gender.FEMALE,
                phone="+1234567890",
                country="USA",
                preferred_degree=DegreeLevel.MASTER,
                cgpa_or_percentage=7.5,
                bio="Aspiring computer scientist looking to pursue a Master's degree in Canada or the UK."
            )
            session.add_all([student1_user, student1_profile])
            print("Created Student: student@test.com (Alice Smith)")

            # Student 2: Bob
            student2_id = str(uuid.uuid4())
            student2_user = User(
                id=student2_id,
                email="bob@test.com",
                password_hash=password_hash,
                role=UserRole.STUDENT,
                is_active=True,
                is_verified=True,
            )
            student2_profile = StudentProfile(
                id=str(uuid.uuid4()),
                user_id=student2_id,
                first_name="Bob",
                last_name="Jones",
                gender=Gender.MALE,
                phone="+1987654321",
                country="Canada",
                preferred_degree=DegreeLevel.BACHELOR,
                cgpa_or_percentage=6.5,
                bio="Excited high school graduate looking for Bachelor's opportunities in Australia."
            )
            session.add_all([student2_user, student2_profile])
            print("Created Student: bob@test.com (Bob Jones)")

            # Student 3: Charlie
            student3_id = str(uuid.uuid4())
            student3_user = User(
                id=student3_id,
                email="charlie@test.com",
                password_hash=password_hash,
                role=UserRole.STUDENT,
                is_active=True,
                is_verified=True,
            )
            student3_profile = StudentProfile(
                id=str(uuid.uuid4()),
                user_id=student3_id,
                first_name="Charlie",
                last_name="Brown",
                gender=Gender.OTHER,
                phone="+447700900077",
                country="UK",
                preferred_degree=DegreeLevel.PHD,
                cgpa_or_percentage=8.0,
                bio="Passionate researcher focusing on sustainable energy systems and seeking PhD funding."
            )
            session.add_all([student3_user, student3_profile])
            print("Created Student: charlie@test.com (Charlie Brown)")

            # 3. Create Agency Users & Profiles
            # Agency 1: Elite (Verified)
            agency1_id = str(uuid.uuid4())
            agency1_user = User(
                id=agency1_id,
                email="agency@test.com",
                password_hash=password_hash,
                role=UserRole.AGENCY,
                is_active=True,
                is_verified=True,
            )
            agency1_profile = Agency(
                id=str(uuid.uuid4()),
                user_id=agency1_id,
                agency_name="Elite Global Education",
                phone="+442079460192",
                country="UK",
                email="agency@test.com",
                description="Top-tier agency helping international students apply to top universities globally.",
                website="https://eliteglobaledu.com",
                verification_status=AgencyVerificationStatus.VERIFIED,
                verified_at=datetime.now(timezone.utc)
            )
            session.add_all([agency1_user, agency1_profile])
            print("Created Agency: agency@test.com (Elite Global Education - Verified)")

            # Agency 2: Pending
            agency2_id = str(uuid.uuid4())
            agency2_user = User(
                id=agency2_id,
                email="pending_agency@test.com",
                password_hash=password_hash,
                role=UserRole.AGENCY,
                is_active=True,
                is_verified=True,
            )
            agency2_profile = Agency(
                id=str(uuid.uuid4()),
                user_id=agency2_id,
                agency_name="Bridge Overseas Study",
                phone="+16045550199",
                country="Canada",
                email="pending_agency@test.com",
                description="Connecting ambitious students with North American academic paths.",
                website="https://bridgeoverseasstudy.ca",
                verification_status=AgencyVerificationStatus.PENDING
            )
            session.add_all([agency2_user, agency2_profile])
            print("Created Agency: pending_agency@test.com (Bridge Overseas Study - Pending)")

            # Agency 3: Rejected
            agency3_id = str(uuid.uuid4())
            agency3_user = User(
                id=agency3_id,
                email="rejected_agency@test.com",
                password_hash=password_hash,
                role=UserRole.AGENCY,
                is_active=True,
                is_verified=True,
            )
            agency3_profile = Agency(
                id=str(uuid.uuid4()),
                user_id=agency3_id,
                agency_name="FastTrack Visa Experts",
                phone="+61298765432",
                country="Australia",
                email="rejected_agency@test.com",
                description="Fast-track applications and visa consultancy service.",
                website="https://fasttrackvisaexperts.com",
                verification_status=AgencyVerificationStatus.REJECTED
            )
            session.add_all([agency3_user, agency3_profile])
            print("Created Agency: rejected_agency@test.com (FastTrack Visa Experts - Rejected)")

            # 4. Create Universities
            uni1 = University(
                id=str(uuid.uuid4()),
                name="University of Toronto",
                location="Canada",
                ranking="Top 50",
                type="Public",
                tuition_category="High",
                programs=["Computer Science", "Business", "Engineering"]
            )
            uni2 = University(
                id=str(uuid.uuid4()),
                name="University of Melbourne",
                location="Australia",
                ranking="Top 100",
                type="Public",
                tuition_category="Medium",
                programs=["Data Science", "Arts", "Law"]
            )
            uni3 = University(
                id=str(uuid.uuid4()),
                name="MIT",
                location="USA",
                ranking="Top 10",
                type="Private",
                tuition_category="High",
                programs=["Engineering", "Computer Science", "Physics"]
            )
            uni4 = University(
                id=str(uuid.uuid4()),
                name="Imperial College London",
                location="UK",
                ranking="Top 20",
                type="Public",
                tuition_category="High",
                programs=["Engineering", "Medicine", "Natural Sciences"]
            )
            session.add_all([uni1, uni2, uni3, uni4])
            print("Created 4 Universities.")

            # 5. Create Scholarships
            # Scholarship 1 (Active, Bachelor, UK, Elite)
            sch1 = Scholarship(
                id=str(uuid.uuid4()),
                title="Excellence in Engineering Scholarship",
                country="UK",
                university="Imperial College London",
                degree_level=DegreeLevel.BACHELOR,
                funding_type=FundingType.FULLY_FUNDED,
                amount=50000.00,
                currency="GBP",
                is_active=True,
                agency_id=agency1_profile.id,
                description="Fully funded engineering scholarship for outstanding undergraduate international applicants.",
                eligibility="Requires 7.5+ IELTS, high school GPA of 3.8+ or equivalent."
            )
            # Scholarship 2 (Active, Bachelor, Australia, Elite)
            sch2 = Scholarship(
                id=str(uuid.uuid4()),
                title="International Student Fund",
                country="Australia",
                university="University of Melbourne",
                degree_level=DegreeLevel.BACHELOR,
                funding_type=FundingType.PARTIAL,
                amount=15000.00,
                currency="AUD",
                is_active=True,
                agency_id=agency1_profile.id,
                description="Partial tuition support for undergraduate students demonstrating financial need and strong academics.",
                eligibility="Open to all international undergraduate programs. Minimum IELTS 6.5."
            )
            # Scholarship 3 (Active, Master, Canada, Elite)
            sch3 = Scholarship(
                id=str(uuid.uuid4()),
                title="Global Excellence Graduate Grant",
                country="Canada",
                university="University of Toronto",
                degree_level=DegreeLevel.MASTER,
                funding_type=FundingType.PARTIAL,
                amount=20000.00,
                currency="CAD",
                is_active=True,
                agency_id=agency1_profile.id,
                description="Merit-based partial funding for international candidates enrolling in postgraduate research programs.",
                eligibility="Enrolled in Master's research program at U of T. Minimum cgpa equivalent to 3.5/4.0."
            )
            # Scholarship 4 (Inactive, Master, USA, Bridge)
            sch4 = Scholarship(
                id=str(uuid.uuid4()),
                title="Expired Merit Scholarship",
                country="USA",
                university="MIT",
                degree_level=DegreeLevel.MASTER,
                funding_type=FundingType.FULLY_FUNDED,
                amount=65000.00,
                currency="USD",
                is_active=False,
                agency_id=agency2_profile.id,
                description="Historic fully funded scholarship for postgraduate computer science students.",
                eligibility="Closed. No longer accepting applications."
            )
            session.add_all([sch1, sch2, sch3, sch4])
            print("Created 4 Scholarships (3 active, 1 inactive).")

            # 6. Create Leads (Applications)
            # Lead 1: Alice applied to Engineering (UK) -> Status: NEW ("submitted")
            lead1 = Lead(
                id=str(uuid.uuid4()),
                student_id=student1_profile.id,
                agency_id=agency1_profile.id,
                scholarship_id=sch1.id,
                status=LeadStatus.NEW,
                notes='{"motivation_letter": "I want this scholarship to solve infrastructure issues back home.", "documents": "CV_Alice.pdf", "notes": "Alice is ready for UK study."}'
            )
            # Lead 2: Alice applied to Graduate Grant (Canada) -> Status: CONTACTED ("under_review")
            lead2 = Lead(
                id=str(uuid.uuid4()),
                student_id=student1_profile.id,
                agency_id=agency1_profile.id,
                scholarship_id=sch3.id,
                status=LeadStatus.CONTACTED,
                notes='{"motivation_letter": "Canada offers the best computer science research environment.", "documents": "Transcript_Alice.pdf", "notes": "Interview scheduled."}'
            )
            # Lead 3: Bob applied to Engineering (UK) -> Status: WON ("accepted")
            lead3 = Lead(
                id=str(uuid.uuid4()),
                student_id=student2_profile.id,
                agency_id=agency1_profile.id,
                scholarship_id=sch1.id,
                status=LeadStatus.WON,
                notes='{"motivation_letter": "I am passionate about building renewable systems.", "documents": "CV_Bob.pdf, Essay_Bob.pdf", "notes": "Offer letter sent."}'
            )
            # Lead 4: Charlie applied to Graduate Grant (Canada) -> Status: LOST ("rejected")
            lead4 = Lead(
                id=str(uuid.uuid4()),
                student_id=student3_profile.id,
                agency_id=agency1_profile.id,
                scholarship_id=sch3.id,
                status=LeadStatus.LOST,
                notes='{"motivation_letter": "I seek research funding for doctoral research.", "documents": "Proposal_Charlie.pdf", "notes": "Academics did not meet minimum criteria."}'
            )
            session.add_all([lead1, lead2, lead3, lead4])
            print("Created 4 Leads/Applications (1 submitted, 1 under review, 1 accepted, 1 rejected).")

            await session.commit()
            print("Database seeded successfully with realistic development data!")
            print("="*60)
            print("TEST LOGINS (all passwords are 'password123'):")
            print("Admin: admin@test.com")
            print("Agency (Verified): agency@test.com")
            print("Agency (Pending): pending_agency@test.com")
            print("Agency (Rejected): rejected_agency@test.com")
            print("Student (Alice): student@test.com")
            print("Student (Bob): bob@test.com")
            print("Student (Charlie): charlie@test.com")
            print("="*60)

        except Exception as e:
            await session.rollback()
            print(f"Failed to seed database: {e}")


if __name__ == "__main__":
    asyncio.run(seed_database())
