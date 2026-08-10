from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AgencyVerificationStatus


class Agency(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Educational Agency profile linked 1-to-1 with a User.
    """

    __tablename__ = "agencies"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    agency_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)

    email: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    country: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    verification_status: Mapped[AgencyVerificationStatus] = mapped_column(
        Enum(AgencyVerificationStatus),
        default=AgencyVerificationStatus.PENDING,
        index=True,
        nullable=False,
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="agency_profile")
    leads = relationship("Lead", back_populates="agency", cascade="all, delete-orphan")
    scholarships = relationship(
        "Scholarship", back_populates="agency", cascade="all, delete-orphan"
    )


    def __repr__(self) -> str:
        return f"<Agency {self.agency_name} (Status: {self.verification_status.value})>"
