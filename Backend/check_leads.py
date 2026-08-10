import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.lead import Lead
from app.models.student_profile import StudentProfile


async def check_db():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(StudentProfile))
        profiles = result.scalars().all()
        print("Student Profiles in DB:")
        for p in profiles:
            print(f"- {p.first_name} {p.last_name} (Profile ID: {p.id}, User ID: {p.user_id})")
            
        result = await session.execute(select(Lead))
        leads = result.scalars().all()
        print("\nLeads in DB:")
        for l in leads:
            print(f"- Lead ID: {l.id}, Student ID: {l.student_id}, Scholarship ID: {l.scholarship_id}")

if __name__ == "__main__":
    asyncio.run(check_db())
