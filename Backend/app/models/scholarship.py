from sqlalchemy import Boolean, Column, Date, Enum, Numeric, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DegreeLevel, FundingType


class Scholarship(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Scholarship opportunities that students can apply to.
    """

    __tablename__ = "scholarships"

    title = Column(String(255), nullable=False)
    country = Column(String(100), index=True, nullable=False)
    university = Column(String(255), nullable=True)

    degree_level = Column(Enum(DegreeLevel), nullable=False)
    funding_type = Column(Enum(FundingType), nullable=False)

    amount = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(10), nullable=True)

    deadline = Column(Date, index=True, nullable=True)
    eligibility = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    application_link = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    agency_id = Column(
        String(36),
        ForeignKey("agencies.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    agency = relationship("Agency", back_populates="scholarships")
    leads = relationship(
        "Lead", back_populates="scholarship", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Scholarship {self.title} ({self.country})>"

