import asyncio
import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.database import AsyncSessionLocal
from app.models.agency import Agency


async def create_missing_agency():
    async with AsyncSessionLocal() as session:
        agency = Agency(
            id=str(uuid.uuid4()),
            user_id='0d42fad5-dbb2-4ec0-a079-2108402d0030',
            agency_name='Test Agency Profile',
            phone='+1234567890',
            country='USA',
            email='test.agency@example.com'
        )
        session.add(agency)
        await session.commit()
        print("Successfully created missing agency profile.")

if __name__ == "__main__":
    asyncio.run(create_missing_agency())
