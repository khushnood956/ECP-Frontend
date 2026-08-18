import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.append("E:/friends/Noman/ECP-main/Backend")
from app.db.database import AsyncSessionLocal
from app.models.lead import Lead
from app.models.enums import LeadStatus
from sqlalchemy import select
from app.schemas.lead import LeadPatchRequest
from app.models.user import User
from app.models.enums import UserRole

async def main():
    async with AsyncSessionLocal() as session:
        stmt = select(Lead).limit(1)
        res = await session.execute(stmt)
        lead = res.scalar_one_or_none()
        if lead:
            from app.services.lead_service import LeadService
            from app.repositories.lead_repository import LeadRepository
            from app.repositories.agency_repository import AgencyRepository
            from app.repositories.transaction import TransactionManager
            
            repo = LeadRepository(session)
            agency_repo = AgencyRepository(session)
            tm = TransactionManager(session)
            service = LeadService(repo, agency_repo, tm)
            
            # Simulate agency user
            stmt = select(User).where(User.role == UserRole.AGENCY).limit(1)
            res = await session.execute(stmt)
            user = res.scalar_one_or_none()
            if not user:
                print("No agency user")
                return

            print(f"Updating lead {lead.id} with agency user {user.id}")
            # Patch request
            req = LeadPatchRequest(status="under_review")
            
            try:
                updated = await service.update(lead.id, req, user)
                
                from app.schemas.lead import LeadResponse
                resp = LeadResponse.model_validate(updated)
                print("response", resp.model_dump())
            except Exception as e:
                import traceback
                traceback.print_exc()
        else:
            print("No leads found")

asyncio.run(main())
