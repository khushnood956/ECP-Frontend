from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student_profile import StudentProfile
from app.repositories.base import BaseRepository
from app.repositories.params import PaginatedResult, PaginationParams


class StudentProfileRepository(BaseRepository[StudentProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=StudentProfile, session=session)

    async def get_by_user_id(self, user_id: UUID | str) -> StudentProfile | None:
        stmt = select(self.model).where(self.model.user_id == str(user_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_scoped(
        self,
        pagination: PaginationParams,
        user_role: str,
        own_agency_id: str | None = None,
        user_id: str | None = None
    ) -> PaginatedResult[StudentProfile]:
        import math

        from sqlalchemy import exists, func

        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)

        from app.models.enums import LeadStatus, UserRole
        from app.models.lead import Lead

        if user_role == UserRole.ADMIN:
            pass
        elif user_role == UserRole.STUDENT:
            if user_id:
                cond = self.model.user_id == str(user_id)
                stmt = stmt.where(cond)
                count_stmt = count_stmt.where(cond)
            else:
                stmt = stmt.where(self.model.id == None)
                count_stmt = count_stmt.where(self.model.id == None)
        elif user_role == UserRole.AGENCY:
            if own_agency_id:
                # Scoped to active leads only (not LeadStatus.LOST)
                lead_exists = exists().where(
                    Lead.student_id == self.model.id,
                    Lead.agency_id == own_agency_id,
                    Lead.status != LeadStatus.LOST
                )
                stmt = stmt.where(lead_exists)
                count_stmt = count_stmt.where(lead_exists)
            else:
                stmt = stmt.where(self.model.id == None)
                count_stmt = count_stmt.where(self.model.id == None)
        else:
            stmt = stmt.where(self.model.id == None)
            count_stmt = count_stmt.where(self.model.id == None)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (pagination.page - 1) * pagination.page_size
        stmt = stmt.offset(offset).limit(pagination.page_size)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        total_pages = (
            math.ceil(total / pagination.page_size)
            if pagination.page_size > 0
            else 0
        )

        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )
