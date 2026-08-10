from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DegreeLevel, FundingType


class Scholarship(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Scholarship opportunities that students can apply to.
    """

    __tablename__ = "scholarships"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    university: Mapped[str | None] = mapped_column(String(255), nullable=True)

    degree_level: Mapped[DegreeLevel] = mapped_column(Enum(DegreeLevel), nullable=False)
    funding_type: Mapped[FundingType] = mapped_column(Enum(FundingType), nullable=False)

    amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    deadline: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)
    eligibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    agency_id: Mapped[str | None] = mapped_column(
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

