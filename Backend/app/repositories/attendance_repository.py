import math
from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic_class import Class
from app.models.attendance import Attendance
from app.models.enums import LeadStatus, UserRole
from app.models.lead import Lead
from app.models.student_profile import StudentProfile
from app.repositories.base import BaseRepository
from app.repositories.params import PaginatedResult, PaginationParams


class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Attendance, session=session)

    async def list_scoped(
        self,
        pagination: PaginationParams,
        user_role: UserRole,
        user_id: UUID | str,
        own_agency_id: str | None = None
    ) -> PaginatedResult[Attendance]:
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)

        if user_role == UserRole.ADMIN:
            pass
        elif user_role == UserRole.TEACHER:
            class_exists = exists().where(
                self.model.class_id == Class.id,
                Class.instructor_id == str(user_id)
            )
            stmt = stmt.where(class_exists)
            count_stmt = count_stmt.where(class_exists)
        elif user_role == UserRole.STUDENT:
            student_exists = exists().where(
                self.model.student_id == StudentProfile.id,
                StudentProfile.user_id == str(user_id)
            )
            stmt = stmt.where(student_exists)
            count_stmt = count_stmt.where(student_exists)
        elif user_role == UserRole.AGENCY:
            if own_agency_id:
                lead_exists = exists().where(
                    Lead.student_id == self.model.student_id,
                    Lead.agency_id == str(own_agency_id),
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
