import os
import uuid
from typing import Any, ClassVar
from uuid import UUID

from app.core.config.settings import settings
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.student_profile_repository import StudentProfileRepository
from app.repositories.transaction import TransactionManager
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityNotFound,
    PermissionDenied,
)
from app.services.storage_service import S3StorageService


class DocumentService(BaseService[Document, Any, Any]):
    repository: DocumentRepository

    ALLOWED_MIME_TYPES: ClassVar[set[str]] = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
        "image/jpg"
    }
    ALLOWED_EXTENSIONS: ClassVar[set[str]] = {".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"}

    def __init__(
        self,
        repository: DocumentRepository,
        student_repository: StudentProfileRepository,
        transaction_manager: TransactionManager,
    ):
        super().__init__(repository=repository, transaction_manager=transaction_manager)
        self.student_repository = student_repository
        self.storage = S3StorageService()

    def validate_file(self, filename: str, content_type: str, file_size: int) -> None:
        # 1. Check file size
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise BusinessRuleViolation(f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB.")

        # 2. Check extension
        _, ext = os.path.splitext(filename.lower())
        if ext not in self.ALLOWED_EXTENSIONS:
            raise BusinessRuleViolation(f"File extension '{ext}' is not allowed.")

        # 3. Check content type
        if content_type not in self.ALLOWED_MIME_TYPES:
            raise BusinessRuleViolation(f"Content type '{content_type}' is not allowed.")

    async def create_document(
        self,
        filename: str,
        content_type: str,
        doc_type: str,
        file_content: bytes,
        user: Any
    ) -> Document:
        from app.models.enums import UserRole
        if user is None:
            raise PermissionDenied("Authentication is required to upload documents.")
        if user.role != UserRole.STUDENT:
            raise PermissionDenied("Only student users can upload documents.")

        student_profile = await self.student_repository.get_by_user_id(user.id)
        if not student_profile:
            raise PermissionDenied("Student profile does not exist. Please create a profile first.")

        # Validate file properties
        file_size = len(file_content)
        self.validate_file(filename, content_type, file_size)

        # Generate ownership-safe S3 object key
        doc_id = str(uuid.uuid4())
        _, ext = os.path.splitext(filename.lower())
        s3_key = f"students/{student_profile.id}/documents/{doc_id}{ext}"

        # Upload file content to S3
        s3_success = await self.storage.upload(file_content, s3_key, content_type)
        if not s3_success:
            raise BusinessRuleViolation("Failed to upload file to storage server.")

        # Insert metadata into PostgreSQL
        db_data = {
            "id": doc_id,
            "student_profile_id": str(student_profile.id),
            "filename": filename,
            "doc_type": doc_type,
            "verified": False,
            "s3_key": s3_key,
            "file_size": file_size,
            "mime_type": content_type
        }

        try:
            async with self.transaction_manager.transaction():
                model_instance = Document(**db_data)
                return await self.repository.create(model_instance)
        except Exception:
            # Clean up the S3 object if database write fails
            await self.storage.delete(s3_key)
            raise

    async def get_by_id(self, id: UUID, user: Any = None) -> Document | None:
        doc = await self.repository.get_by_id(id)
        if not doc:
            return None

        if user is not None:
            from app.models.enums import UserRole
            if user.role == UserRole.STUDENT:
                student_profile = await self.student_repository.get_by_user_id(user.id)
                if not student_profile or str(doc.student_profile_id) != str(student_profile.id):
                    raise PermissionDenied("You do not have permission to view this document.")
            elif user.role == UserRole.AGENCY:
                raise PermissionDenied("Agencies are not allowed to access student documents directly.")
        return doc

    async def get_download_url(self, id: UUID, user: Any) -> str:
        doc = await self.get_by_id(id, user)
        if not doc:
            raise EntityNotFound(f"Document with id {id} not found.")

        url = await self.storage.generate_download_url(
            doc.s3_key,
            doc.filename,
            expires_in=settings.S3_PRESIGNED_EXPIRY
        )
        return url

    async def list_documents(self, user: Any) -> list[Document]:
        from app.models.enums import UserRole
        if user.role == UserRole.STUDENT:
            student_profile = await self.student_repository.get_by_user_id(user.id)
            if not student_profile:
                return []
            return await self.repository.get_by_student_profile_id(student_profile.id)
        elif user.role == UserRole.ADMIN:
            result = await self.repository.list()
            return list(result)
        else:
            raise PermissionDenied("You do not have permission to list documents.")

    async def delete(self, id: UUID, user: Any = None) -> bool:
        doc = await self.repository.get_by_id(id)
        if not doc:
            raise EntityNotFound(f"Document with id {id} not found.")

        if user is not None:
            from app.models.enums import UserRole
            if user.role == UserRole.STUDENT:
                student_profile = await self.student_repository.get_by_user_id(user.id)
                if not student_profile or str(doc.student_profile_id) != str(student_profile.id):
                    raise PermissionDenied("You do not have permission to delete this document.")
            elif user.role != UserRole.ADMIN:
                raise PermissionDenied("You do not have permission to delete this document.")

        s3_delete_success = await self.storage.delete(doc.s3_key)
        if not s3_delete_success:
            raise BusinessRuleViolation("Failed to delete document from storage server.")

        async with self.transaction_manager.transaction():
            return await self.repository.delete(id)
