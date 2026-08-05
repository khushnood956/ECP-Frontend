from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import LeadStatus


class Lead(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A Lead links a Student to a Scholarship, optionally facilitated by an Agency.
    """

    __tablename__ = "leads"

    student_id = Column(
        String(36),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    agency_id = Column(
        String(36), ForeignKey("agencies.id", ondelete="SET NULL"), nullable=True
    )
    scholarship_id = Column(
        String(36), ForeignKey("scholarships.id", ondelete="CASCADE"), nullable=False
    )

    status = Column(
        Enum(LeadStatus), default=LeadStatus.NEW, index=True, nullable=False
    )
    notes = Column(Text, nullable=True)

    status_updated_at = Column(DateTime(timezone=True), nullable=True)
    follow_up_date = Column(DateTime(timezone=True), index=True, nullable=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="leads")
    agency = relationship("Agency", back_populates="leads")
    scholarship = relationship("Scholarship", back_populates="leads")

    def __repr__(self) -> str:
        return f"<Lead (Student: {self.student_id}, Scholarship: {self.scholarship_id}, Status: {self.status.value})>"
