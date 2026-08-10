import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.agency import Agency
from app.models.user import User


async def check_db():
    async with AsyncSessionLocal() as session:
        # Check users
        result = await session.execute(select(User))
        users = result.scalars().all()
        print("Users in DB:")
        for u in users:
            print(f"- {u.email} (ID: {u.id}, Role: {u.role})")
            
        # Check agencies
        result = await session.execute(select(Agency))
        agencies = result.scalars().all()
        print("\nAgencies in DB:")
        for a in agencies:
            print(f"- {a.agency_name} (ID: {a.id}, User ID: {a.user_id})")

if __name__ == "__main__":
    asyncio.run(check_db())
