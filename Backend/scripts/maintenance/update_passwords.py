import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import update

from app.core.security import get_password_hash
from app.db.database import AsyncSessionLocal
from app.models.user import User


async def update_passwords():
    async with AsyncSessionLocal() as session:
        new_hash = get_password_hash("password123")
        await session.execute(
            update(User)
            .where(User.email.in_(["admin@test.com", "student@test.com", "agency@test.com"]))
            .values(password_hash=new_hash)
        )
        await session.commit()
        print("Passwords updated successfully to 'password123'")

if __name__ == "__main__":
    asyncio.run(update_passwords())
