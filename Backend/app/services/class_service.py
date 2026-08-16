from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.models.academic_class import Class
from app.models.enrollment import Enrollment
from app.models.enums import UserRole
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.repositories.class_repository import ClassRepository
from app.repositories.params import PaginationParams
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityNotFound,
    PermissionDenied,
)


class ClassService(BaseService[Class, Any, Any]):
    def __init__(self, repository: ClassRepository, transaction_manager: Any):
        super().__init__(repository=repository, transaction_manager=transaction_manager)

    async def list_classes(self, user: User, pagination: PaginationParams) -> Any:
        return await self.repository.list_scoped(pagination, user.role, user.id)  # type: ignore

    async def get_by_id_scoped(self, id: UUID, user: User) -> Class | None:
        cls_obj = await self.repository.get_by_id(id)
        if not cls_obj:
            return None

        # Scope verification
        if user.role == UserRole.ADMIN:
            return cls_obj
        elif user.role == UserRole.TEACHER:
            if str(cls_obj.instructor_id) != str(user.id):
                raise PermissionDenied("You do not have permission to access this class.")
            return cls_obj
        elif user.role == UserRole.STUDENT:
            # Check if enrolled
            from sqlalchemy import exists
            student_stmt = select(StudentProfile.id).where(StudentProfile.user_id == str(user.id))
            student_res = await self.repository.session.execute(student_stmt)  # type: ignore
            student_id = student_res.scalar_one_or_none()
            if not student_id:
                raise PermissionDenied("Student profile not found.")
            
            enrolled_stmt = select(exists().where(
                Enrollment.class_id == str(cls_obj.id),
                Enrollment.student_id == str(student_id)
            ))
            enrolled = (await self.repository.session.execute(enrolled_stmt)).scalar()  # type: ignore
            if not enrolled:
                raise PermissionDenied("You are not enrolled in this class.")
            return cls_obj
        else:
            raise PermissionDenied("You do not have permission to access this class.")

    async def create(self, obj_in: Any, user: Any = None) -> Class:
        if not user or user.role != UserRole.ADMIN:
            raise PermissionDenied("Only administrators can create classes.")

        async with self.transaction_manager.transaction():
            data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else dict(obj_in)
            
            # Validate instructor
            instructor_id = data.get("instructor_id")
            if not instructor_id:
                raise BusinessRuleViolation("Instructor ID is required.")
                
            instructor_stmt = select(User).where(User.id == str(instructor_id))
            instructor_res = await self.repository.session.execute(instructor_stmt)  # type: ignore
            instructor = instructor_res.scalar_one_or_none()
            if not instructor:
                raise EntityNotFound(f"Instructor with ID {instructor_id} not found.")
            if instructor.role != UserRole.TEACHER:
                raise BusinessRuleViolation("Instructor must be a teacher.")

            # Validate unique class code
            code = data.get("code")
            existing_stmt = select(Class).where(Class.code == code)
            existing_res = await self.repository.session.execute(existing_stmt)  # type: ignore
            if existing_res.scalar_one_or_none():
                raise BusinessRuleViolation(f"Class with code {code} already exists.")

            model_instance = Class(**data)
            return await self.repository.create(model_instance)

    async def update(self, id: UUID, obj_in: Any, user: Any = None) -> Class | None:
        if not user:
            raise PermissionDenied("User credentials required.")
        async with self.transaction_manager.transaction():
            cls_obj = await self._require_entity(id)
            if user.role != UserRole.ADMIN and str(cls_obj.instructor_id) != str(user.id):
                raise PermissionDenied("You do not have permission to update this class.")

            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else dict(obj_in)
            )
            # Mass assignment protection
            update_data.pop("id", None)
            update_data.pop("instructor_id", None)

            return await self.repository.update(id, update_data)

    async def delete(self, id: UUID, user: Any = None) -> bool:
        if not user:
            raise PermissionDenied("User credentials required.")
        async with self.transaction_manager.transaction():
            cls_obj = await self._require_entity(id)
            if user.role != UserRole.ADMIN and str(cls_obj.instructor_id) != str(user.id):
                raise PermissionDenied("You do not have permission to delete this class.")
            return await self.repository.delete(id)
