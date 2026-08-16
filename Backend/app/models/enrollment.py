from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import EnrollmentStatus


class Enrollment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Enrollment model linking a student to a class.
    """

    __tablename__ = "enrollments"

    class_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.ACTIVE
    )

    # Relationships
    academic_class = relationship("Class", back_populates="enrollments")
    student = relationship("StudentProfile")

    __table_args__ = (
        UniqueConstraint("class_id", "student_id", name="uq_class_student_enrollment"),
    )

    def __repr__(self) -> str:
        return f"<Enrollment Student: {self.student_id} Class: {self.class_id} ({self.status.value})>"
