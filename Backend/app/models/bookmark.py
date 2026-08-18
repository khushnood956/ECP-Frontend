from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Bookmark(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Bookmark database model for students saving scholarships or universities.
    """

    __tablename__ = "bookmarks"

    student_profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    bookmark_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "scholarship" or "university"

    scholarship_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("scholarships.id", ondelete="CASCADE"),
        nullable=True,
    )

    university_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("universities.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Relationships
    student = relationship("StudentProfile", back_populates="bookmarks")
    scholarship = relationship("Scholarship")
    university = relationship("University")

    __table_args__ = (
        UniqueConstraint(
            "student_profile_id",
            "scholarship_id",
            name="uq_student_scholarship_bookmark",
        ),
        UniqueConstraint(
            "student_profile_id",
            "university_id",
            name="uq_student_university_bookmark",
        ),
    )

    def __repr__(self) -> str:
        return f"<Bookmark {self.bookmark_type} for student {self.student_profile_id}>"
