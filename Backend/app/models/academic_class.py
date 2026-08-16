from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Class(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Academic Class model representing a course or class taught by an instructor.
    """

    __tablename__ = "classes"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    instructor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # Relationships
    instructor = relationship("User", foreign_keys=[instructor_id])
    enrollments = relationship(
        "Enrollment",
        back_populates="academic_class",
        cascade="all, delete-orphan",
    )
    attendances = relationship(
        "Attendance",
        back_populates="academic_class",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Class {self.name} ({self.code})>"
