from sqlalchemy import Column, String, Date, Text, ForeignKey, Enum, Float, Numeric
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from app.models.enums import Gender, DegreeLevel

class StudentProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Student profile linked 1-to-1 with a User.
    """
    __tablename__ = "student_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    country = Column(String(100), index=True, nullable=True)
    city = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    
    highest_qualification = Column(String(255), nullable=True)
    cgpa_or_percentage = Column(Float, nullable=True)
    preferred_degree = Column(Enum(DegreeLevel), nullable=True)
    preferred_country = Column(String(100), nullable=True)
    budget = Column(Numeric(12, 2), nullable=True)
    
    bio = Column(Text, nullable=True)
    profile_picture_url = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    leads = relationship("Lead", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<StudentProfile {self.first_name} {self.last_name}>"
