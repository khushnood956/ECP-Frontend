from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ScholarshipApplicationRequirement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Defines a single requirement for applying to a scholarship.
    """
    __tablename__ = "scholarship_application_requirements"

    scholarship_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scholarships.id", ondelete="CASCADE"), nullable=False
    )
    
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. text, textarea, file, select
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    options: Mapped[str | None] = mapped_column(Text, nullable=True) # JSON string for choices if any
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)

    scholarship = relationship("Scholarship", back_populates="application_requirements")


class StudentApplicationResponse(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A student's answer to a specific requirement for a scholarship lead.
    """
    __tablename__ = "student_application_responses"

    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    requirement_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scholarship_application_requirements.id", ondelete="CASCADE"), nullable=False
    )
    
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    lead = relationship("Lead", back_populates="application_responses")
    requirement = relationship("ScholarshipApplicationRequirement")
