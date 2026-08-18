from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Documents uploaded by students for verification/applications.
    """
    __tablename__ = "student_documents"

    student_profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    upload_date: Mapped[date] = mapped_column(Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    
    # S3 binary storage fields
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    student = relationship("StudentProfile", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document {self.filename} ({self.doc_type})>"
