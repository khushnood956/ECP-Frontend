from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.models.academic_class import Class
from app.models.attendance import Attendance
from app.models.enrollment import Enrollment
from app.models.enums import EnrollmentStatus, LeadStatus, UserRole
from app.models.lead import Lead
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.params import PaginationParams
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityNotFound,
    PermissionDenied,
)

# Baseline configuration constant
ATTENDANCE_EDIT_WINDOW_DAYS = 7


class AttendanceService(BaseService[Attendance, Any, Any]):
    def __init__(self, repository: AttendanceRepository, transaction_manager: Any):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    async def _get_user_agency_id(self, user: User) -> str | None:
        if user.role != UserRole.AGENCY:
            return None

        try:
            from app.models.agency import Agency
            stmt = select(Agency).where(Agency.user_id == str(user.id))
            result = await self.repository.session.execute(stmt)  # type: ignore
            agency = result.scalar_one_or_none()
            if agency:
                return str(agency.id)
        except Exception:  # noqa: BLE001, S110
            pass
        return None

    async def list_attendance(self, user: User, pagination: PaginationParams) -> Any:
        own_agency_id = await self._get_user_agency_id(user)
        return await self.repository.list_scoped(pagination, user.role, user.id, own_agency_id)  # type: ignore

    async def get_by_id_scoped(self, id: UUID, user: User) -> Attendance | None:
        attendance = await self.repository.get_by_id(id)
        if not attendance:
            return None

        if user.role == UserRole.ADMIN:
            return attendance
        elif user.role == UserRole.TEACHER:
            class_stmt = select(Class).where(Class.id == str(attendance.class_id))
            class_res = await self.repository.session.execute(class_stmt)  # type: ignore
            cls_obj = class_res.scalar_one_or_none()
            if not cls_obj or str(cls_obj.instructor_id) != str(user.id):
                raise PermissionDenied("You do not have permission to view this attendance record.")
            return attendance
        elif user.role == UserRole.STUDENT:
            student_stmt = select(StudentProfile).where(StudentProfile.id == str(attendance.student_id))
            student_res = await self.repository.session.execute(student_stmt)  # type: ignore
            student = student_res.scalar_one_or_none()
            if not student or str(student.user_id) != str(user.id):
                raise PermissionDenied("You do not have permission to view this attendance record.")
            return attendance
        elif user.role == UserRole.AGENCY:
            own_agency_id = await self._get_user_agency_id(user)
            if not own_agency_id:
                raise PermissionDenied("You do not have permission to view this attendance record.")
            # Check Lead connection
            lead_stmt = select(Lead.id).where(
                Lead.student_id == str(attendance.student_id),
                Lead.agency_id == own_agency_id,
                Lead.status != LeadStatus.LOST
            )
            lead_res = await self.repository.session.execute(lead_stmt)  # type: ignore
            if not lead_res.scalar_one_or_none():
                raise PermissionDenied("You do not have permission to view this attendance record.")
            return attendance
        else:
            raise PermissionDenied("You do not have permission to view this attendance record.")

    async def create(self, obj_in: Any, user: Any = None) -> Attendance:
        if not user or user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            raise PermissionDenied("You do not have permission to create attendance records.")

        async with self.transaction_manager.transaction():
            data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else dict(obj_in)
            class_id = data.get("class_id")
            student_id = data.get("student_id")
            record_date = data.get("date")

            if not record_date:
                raise BusinessRuleViolation("Attendance date is required.")

            # Date validation: reject future attendance date (date > current UTC date)
            from datetime import date as dt_date
            if isinstance(record_date, str):
                record_date = dt_date.fromisoformat(record_date)
            elif isinstance(record_date, datetime):
                record_date = record_date.date()

            today_utc = datetime.now(timezone.utc).date()
            if record_date > today_utc:
                raise BusinessRuleViolation("Attendance date cannot be in the future.")

            # Validate class
            class_stmt = select(Class).where(Class.id == str(class_id))
            class_res = await self.repository.session.execute(class_stmt)  # type: ignore
            cls_obj = class_res.scalar_one_or_none()
            if not cls_obj:
                raise EntityNotFound(f"Class with ID {class_id} not found.")

            # Teacher must own class
            if user.role == UserRole.TEACHER and str(cls_obj.instructor_id) != str(user.id):
                raise PermissionDenied("You can only record attendance for classes you teach.")

            # Validate student profile
            student_stmt = select(StudentProfile).where(StudentProfile.id == str(student_id))
            student_res = await self.repository.session.execute(student_stmt)  # type: ignore
            student = student_res.scalar_one_or_none()
            if not student:
                raise EntityNotFound(f"Student profile with ID {student_id} not found.")

            # Student must be enrolled in class
            enrollment_stmt = select(Enrollment).where(
                Enrollment.class_id == str(class_id),
                Enrollment.student_id == str(student_id)
            )
            enrollment_res = await self.repository.session.execute(enrollment_stmt)  # type: ignore
            enrollment = enrollment_res.scalar_one_or_none()
            if not enrollment:
                raise BusinessRuleViolation("Student is not enrolled in this class.")
            
            # Enrollment must be ACTIVE (ACAD-AUDIT-01)
            if enrollment.status != EnrollmentStatus.ACTIVE:
                raise BusinessRuleViolation(f"Cannot record attendance: Enrollment status is {enrollment.status.value}.")

            # Prevent duplicate attendance for class/student/date
            existing_stmt = select(Attendance).where(
                Attendance.class_id == str(class_id),
                Attendance.student_id == str(student_id),
                Attendance.date == record_date
            )
            existing_res = await self.repository.session.execute(existing_stmt)  # type: ignore
            if existing_res.scalar_one_or_none():
                raise BusinessRuleViolation("Attendance record already exists for this student on this date.")

            model_instance = Attendance(**data)
            return await self.repository.create(model_instance)

    async def update(self, id: UUID, obj_in: Any, user: Any = None) -> Attendance | None:
        if not user:
            raise PermissionDenied("User credentials required.")
        async with self.transaction_manager.transaction():
            attendance = await self._require_entity(id)

            # Fetch class to verify ownership
            class_stmt = select(Class).where(Class.id == str(attendance.class_id))
            class_res = await self.repository.session.execute(class_stmt)  # type: ignore
            cls_obj = class_res.scalar_one_or_none()
            if not cls_obj:
                raise EntityNotFound("Class not found.")

            if user.role != UserRole.ADMIN:
                if user.role != UserRole.TEACHER or str(cls_obj.instructor_id) != str(user.id):
                    raise PermissionDenied("You do not have permission to update this attendance record.")

                # Check edit window for teachers
                record_date = attendance.date
                today = datetime.now(timezone.utc).date()
                from datetime import date as dt_date
                if isinstance(record_date, str):
                    record_date = dt_date.fromisoformat(record_date)
                elif isinstance(record_date, datetime):
                    record_date = record_date.date()

                if record_date > today:
                    raise BusinessRuleViolation("Future attendance records cannot be modified.")

                if (today - record_date).days > ATTENDANCE_EDIT_WINDOW_DAYS:
                    raise PermissionDenied("Attendance modification window has expired.")

            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else dict(obj_in)
            )
            # Mass assignment protection
            update_data.pop("id", None)
            update_data.pop("class_id", None)
            update_data.pop("student_id", None)
            update_data.pop("date", None)

            return await self.repository.update(id, update_data)

    async def delete(self, id: UUID, user: Any = None) -> bool:
        if not user:
            raise PermissionDenied("User credentials required.")
        async with self.transaction_manager.transaction():
            attendance = await self._require_entity(id)

            # Fetch class to verify ownership
            class_stmt = select(Class).where(Class.id == str(attendance.class_id))
            class_res = await self.repository.session.execute(class_stmt)  # type: ignore
            cls_obj = class_res.scalar_one_or_none()
            if not cls_obj:
                raise EntityNotFound("Class not found.")

            if user.role != UserRole.ADMIN and (user.role != UserRole.TEACHER or str(cls_obj.instructor_id) != str(user.id)):
                raise PermissionDenied("You do not have permission to delete this attendance record.")

            return await self.repository.delete(id)
