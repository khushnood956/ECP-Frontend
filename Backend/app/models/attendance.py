from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AttendanceStatus


class Attendance(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Attendance model tracking daily student status for a class.
    """

    __tablename__ = "attendances"

    class_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    academic_class = relationship("Class", back_populates="attendances")
    student = relationship("StudentProfile")

    __table_args__ = (
        UniqueConstraint("class_id", "student_id", "date", name="uq_class_student_date_attendance"),
    )

    def __repr__(self) -> str:
        return f"<Attendance Student: {self.student_id} Date: {self.date} Status: {self.status.value}>"
