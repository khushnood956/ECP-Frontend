from datetime import date

from sqlalchemy import Date, Enum, Float, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DegreeLevel, Gender


class StudentProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Student profile linked 1-to-1 with a User.
    """

    __tablename__ = "student_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)

    country: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    highest_qualification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cgpa_or_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_degree: Mapped[DegreeLevel | None] = mapped_column(Enum(DegreeLevel), nullable=True)
    preferred_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    budget: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_picture_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    leads = relationship("Lead", back_populates="student", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="student", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<StudentProfile {self.first_name} {self.last_name}>"
