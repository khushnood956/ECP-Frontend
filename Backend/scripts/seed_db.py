import asyncio
import os
import sys
import uuid

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash
from app.db.database import AsyncSessionLocal
from app.models.agency import Agency
from app.models.enums import DegreeLevel, FundingType, Gender, LeadStatus, UserRole
from app.models.lead import Lead
from app.models.scholarship import Scholarship
from app.models.student_profile import StudentProfile
from app.models.user import User


async def seed_database():
    print("Seeding database with test users...")
    async with AsyncSessionLocal() as session:
        # Create standard password hash for "password123"
        password_hash = get_password_hash("password123")
        
        # 1. Create Admin
        admin_id = str(uuid.uuid4())
        admin_user = User(
            id=admin_id,
            email="admin@test.com",
            password_hash=password_hash,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        
        # 2. Create Student
        student_id = str(uuid.uuid4())
        student_user = User(
            id=student_id,
            email="student@test.com",
            password_hash=password_hash,
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,
        )
        
        student_profile = StudentProfile(
            id=str(uuid.uuid4()),
            user_id=student_id,
            first_name="Alice",
            last_name="Smith",
            gender=Gender.FEMALE,
            phone="+1234567890",
            country="USA",
            preferred_degree=DegreeLevel.BACHELOR
        )
        
        # 3. Create Agency
        agency_id = str(uuid.uuid4())
        agency_user = User(
            id=agency_id,
            email="agency@test.com",
            password_hash=password_hash,
            role=UserRole.AGENCY,
            is_active=True,
            is_verified=True,
        )
        
        agency_profile = Agency(
            id=str(uuid.uuid4()),
            user_id=agency_id,
            agency_name="Global Education Consultants",
            phone="+0987654321",
            country="UK",
            email="agency@test.com"
        )
        
        # 4. Create Scholarship
        scholarship_id = str(uuid.uuid4())
        scholarship = Scholarship(
            id=scholarship_id,
            title="Excellence in Engineering Scholarship",
            country="UK",
            university="Imperial College London",
            degree_level=DegreeLevel.BACHELOR,
            funding_type=FundingType.FULLY_FUNDED,
            amount=50000.00,
            currency="GBP",
            is_active=True
        )

        # 5. Create Lead linking Student -> Scholarship -> Agency
        lead = Lead(
            id=str(uuid.uuid4()),
            student_id=student_profile.id,
            agency_id=agency_profile.id,
            scholarship_id=scholarship.id,
            status=LeadStatus.NEW,
            notes="Student is highly interested."
        )

        try:
            # Check if exists first to avoid duplicates if run multiple times
            from sqlalchemy import select
            
            # Check admin
            result = await session.execute(select(User).where(User.email == "admin@test.com"))
            if not result.scalar_one_or_none():
                session.add(admin_user)
                print(f"Added Admin: {admin_user.email}")
                
            # Check student
            result = await session.execute(select(User).where(User.email == "student@test.com"))
            existing_student = result.scalar_one_or_none()
            if not existing_student:
                session.add(student_user)
                session.add(student_profile)
                print(f"Added Student: {student_user.email} with profile")
            else:
                res = await session.execute(select(StudentProfile).where(StudentProfile.user_id == existing_student.id))
                existing_sp = res.scalar_one_or_none()
                if existing_sp:
                    student_profile.id = existing_sp.id
                
            # Check agency
            result = await session.execute(select(User).where(User.email == "agency@test.com"))
            existing_agency = result.scalar_one_or_none()
            if not existing_agency:
                session.add(agency_user)
                session.add(agency_profile)
                print(f"Added Agency: {agency_user.email} with profile")
            else:
                res = await session.execute(select(Agency).where(Agency.user_id == existing_agency.id))
                existing_ap = res.scalar_one_or_none()
                if existing_ap:
                    agency_profile.id = existing_ap.id
                
            # Recreate lead with updated IDs
            lead.student_id = student_profile.id
            lead.agency_id = agency_profile.id
                
            # Add Scholarship and Lead only if Scholarship doesn't exist
            result = await session.execute(select(Scholarship).where(Scholarship.title == "Excellence in Engineering Scholarship"))
            if not result.scalar_one_or_none():
                session.add(scholarship)
                session.add(lead)
                print("Added Scholarship and Lead")
                
            await session.commit()
            print("Database seeded successfully!")
            print("Login credentials for all users: Password is 'password123'")
            
        except Exception as e:  # noqa: BLE001
            await session.rollback()
            print(f"Failed to seed database: {e}")

if __name__ == "__main__":
    asyncio.run(seed_database())
