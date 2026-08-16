from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.models.academic_class import Class
from app.models.enrollment import Enrollment
from app.models.enums import UserRole
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.params import PaginationParams
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityNotFound,
    PermissionDenied,
)


class EnrollmentService(BaseService[Enrollment, Any, Any]):
    def __init__(self, repository: EnrollmentRepository, transaction_manager: Any):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    async def list_enrollments(self, user: User, pagination: PaginationParams) -> Any:
        return await self.repository.list_scoped(pagination, user.role, user.id)  # type: ignore

    async def get_by_id_scoped(self, id: UUID, user: User) -> Enrollment | None:
        enrollment = await self.repository.get_by_id(id)
        if not enrollment:
            return None

        if user.role == UserRole.ADMIN:
            return enrollment
        elif user.role == UserRole.TEACHER:
            class_stmt = select(Class).where(Class.id == str(enrollment.class_id))
            class_res = await self.repository.session.execute(class_stmt)  # type: ignore
            cls_obj = class_res.scalar_one_or_none()
            if not cls_obj or str(cls_obj.instructor_id) != str(user.id):
                raise PermissionDenied("You do not have permission to view this enrollment.")
            return enrollment
        elif user.role == UserRole.STUDENT:
            student_stmt = select(StudentProfile).where(StudentProfile.id == str(enrollment.student_id))
            student_res = await self.repository.session.execute(student_stmt)  # type: ignore
            student = student_res.scalar_one_or_none()
            if not student or str(student.user_id) != str(user.id):
                raise PermissionDenied("You do not have permission to view this enrollment.")
            return enrollment
        else:
            raise PermissionDenied("You do not have permission to view this enrollment.")

    async def create(self, obj_in: Any, user: Any = None) -> Enrollment:
        if not user or user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            raise PermissionDenied("You do not have permission to create enrollments.")

        async with self.transaction_manager.transaction():
            data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else dict(obj_in)
            class_id = data.get("class_id")
            student_id = data.get("student_id")

            # Validate class
            class_stmt = select(Class).where(Class.id == str(class_id))
            class_res = await self.repository.session.execute(class_stmt)  # type: ignore
            cls_obj = class_res.scalar_one_or_none()
            if not cls_obj:
                raise EntityNotFound(f"Class with ID {class_id} not found.")

            # Teacher must own class
            if user.role == UserRole.TEACHER and str(cls_obj.instructor_id) != str(user.id):
                raise PermissionDenied("You can only enroll students in classes you teach.")

            # Validate student profile
            student_stmt = select(StudentProfile).where(StudentProfile.id == str(student_id))
            student_res = await self.repository.session.execute(student_stmt)  # type: ignore
            student = student_res.scalar_one_or_none()
            if not student:
                raise EntityNotFound(f"Student profile with ID {student_id} not found.")

            # Target user must be a student
            user_stmt = select(User).where(User.id == str(student.user_id))
            user_res = await self.repository.session.execute(user_stmt)  # type: ignore
            target_user = user_res.scalar_one_or_none()
            if not target_user or target_user.role != UserRole.STUDENT:
                raise BusinessRuleViolation("Enrolled user must have STUDENT role.")

            # Prevent duplicate enrollment
            existing_stmt = select(Enrollment).where(
                Enrollment.class_id == str(class_id),
                Enrollment.student_id == str(student_id)
            )
            existing_res = await self.repository.session.execute(existing_stmt)  # type: ignore
            if existing_res.scalar_one_or_none():
                raise BusinessRuleViolation("Student is already enrolled in this class.")

            model_instance = Enrollment(**data)
            return await self.repository.create(model_instance)

    async def update(self, id: UUID, obj_in: Any, user: Any = None) -> Enrollment | None:
        if not user:
            raise PermissionDenied("User credentials required.")
        async with self.transaction_manager.transaction():
            enrollment = await self._require_entity(id)
            
            # Fetch class to verify ownership
            class_stmt = select(Class).where(Class.id == str(enrollment.class_id))
            class_res = await self.repository.session.execute(class_stmt)  # type: ignore
            cls_obj = class_res.scalar_one_or_none()
            if not cls_obj:
                raise EntityNotFound("Class not found.")

            if user.role != UserRole.ADMIN and (user.role != UserRole.TEACHER or str(cls_obj.instructor_id) != str(user.id)):
                raise PermissionDenied("You do not have permission to update this enrollment.")

            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else dict(obj_in)
            )
            # Mass assignment protection
            update_data.pop("id", None)
            update_data.pop("class_id", None)
            update_data.pop("student_id", None)

            return await self.repository.update(id, update_data)

    async def delete(self, id: UUID, user: Any = None) -> bool:
        if not user:
            raise PermissionDenied("User credentials required.")
        async with self.transaction_manager.transaction():
            enrollment = await self._require_entity(id)

            # Fetch class to verify ownership
            class_stmt = select(Class).where(Class.id == str(enrollment.class_id))
            class_res = await self.repository.session.execute(class_stmt)  # type: ignore
            cls_obj = class_res.scalar_one_or_none()
            if not cls_obj:
                raise EntityNotFound("Class not found.")

            if user.role != UserRole.ADMIN and (user.role != UserRole.TEACHER or str(cls_obj.instructor_id) != str(user.id)):
                raise PermissionDenied("You do not have permission to delete this enrollment.")

            return await self.repository.delete(id)
