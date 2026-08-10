import asyncio
import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.agency import Agency
from app.models.user import User


async def fix_missing_agency():
    async with AsyncSessionLocal() as session:
        uid = '873fe828-9649-476d-96ba-94b54d78b147'
        u = await session.execute(select(User).where(User.id == uid))
        user = u.scalar_one_or_none()
        if not user:
            print("User not found!")
            return
            
        a = await session.execute(select(Agency).where(Agency.user_id == uid))
        agency = a.scalar_one_or_none()
        if not agency:
            print("Creating missing agency profile...")
            agency = Agency(
                id=str(uuid.uuid4()),
                user_id=uid,
                agency_name=user.email.split("@")[0],
                email=user.email
            )
            session.add(agency)
            await session.commit()
            print("Agency created with ID:", agency.id)
        else:
            print("Agency already exists:", agency.id)

if __name__ == "__main__":
    asyncio.run(fix_missing_agency())
