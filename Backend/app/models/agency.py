from sqlalchemy import Column, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from app.models.enums import AgencyVerificationStatus

class Agency(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Educational Agency profile linked 1-to-1 with a User.
    """
    __tablename__ = "agencies"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    agency_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    registration_number = Column(String(100), index=True, nullable=True)
    
    email = Column(String(255), index=True, nullable=True)
    phone = Column(String(50), nullable=True)
    
    country = Column(String(100), index=True, nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    verification_status = Column(Enum(AgencyVerificationStatus), default=AgencyVerificationStatus.PENDING, index=True, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="agency_profile")
    leads = relationship("Lead", back_populates="agency", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Agency {self.agency_name} (Status: {self.verification_status.value})>"
