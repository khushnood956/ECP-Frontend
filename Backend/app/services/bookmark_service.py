from typing import Any
from uuid import UUID

from app.models.bookmark import Bookmark
from app.models.user import User
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.student_profile_repository import StudentProfileRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityNotFound,
    PermissionDenied,
)


class BookmarkService(BaseService[Bookmark, Any, Any]):
    repository: BookmarkRepository

    def __init__(
        self,
        repository: BookmarkRepository,
        student_repository: StudentProfileRepository,
        transaction_manager: TransactionManager,
    ):
        super().__init__(repository=repository, transaction_manager=transaction_manager)
        self.student_repository = student_repository

    async def list_bookmarks(self, current_user: User) -> list[Bookmark]:
        student_profile = await self.student_repository.get_by_user_id(current_user.id)
        if not student_profile:
            raise PermissionDenied("User is not registered as a student.")
        return await self.repository.get_by_student_profile_id(student_profile.id)

    async def create_bookmark(
        self,
        bookmark_type: str,
        scholarship_id: UUID | None,
        university_id: UUID | None,
        current_user: User,
    ) -> Bookmark:
        student_profile = await self.student_repository.get_by_user_id(current_user.id)
        if not student_profile:
            raise PermissionDenied("User is not registered as a student.")

        if bookmark_type not in ["scholarship", "university"]:
            raise BusinessRuleViolation("Invalid bookmark type.")

        resource_id = scholarship_id if bookmark_type == "scholarship" else university_id
        if not resource_id:
            raise BusinessRuleViolation("Resource ID is required.")

        # Check for duplicates
        existing = await self.repository.get_by_student_and_resource(
            student_profile.id, bookmark_type, resource_id
        )
        if existing:
            raise BusinessRuleViolation("Bookmark already exists.")

        async with self.transaction_manager.transaction():
            model_instance = Bookmark(
                student_profile_id=student_profile.id,
                bookmark_type=bookmark_type,
                scholarship_id=str(scholarship_id) if scholarship_id else None,
                university_id=str(university_id) if university_id else None,
            )
            bookmark = await self.repository.create(model_instance)
            reloaded = await self.repository.get_by_id(bookmark.id)
            return reloaded or bookmark

    async def delete_bookmark(self, bookmark_id: UUID | str, current_user: User) -> bool:
        student_profile = await self.student_repository.get_by_user_id(current_user.id)
        if not student_profile:
            raise PermissionDenied("User is not registered as a student.")

        uuid_val = UUID(str(bookmark_id))
        bookmark = await self.repository.get_by_id(uuid_val)
        if not bookmark:
            raise EntityNotFound(f"Bookmark with id {bookmark_id} not found.")

        if bookmark.student_profile_id != student_profile.id:
            raise PermissionDenied("You do not have permission to delete this bookmark.")

        async with self.transaction_manager.transaction():
            await self.repository.delete(uuid_val)
            return True
