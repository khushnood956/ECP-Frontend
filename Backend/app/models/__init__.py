"""
Import all models here so that Alembic and SQLAlchemy can discover them automatically via Base.metadata.
Order of imports doesn't matter for metadata, but it avoids circular dependencies inside the models themselves.
"""

from app.models.academic_class import Class
from app.models.agency import Agency
from app.models.attendance import Attendance
from app.models.enrollment import Enrollment
from app.models.lead import Lead
from app.models.scholarship import Scholarship
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.models.university import University

# Expose models for easier imports elsewhere
__all__ = ["Agency", "Attendance", "Class", "Enrollment", "Lead", "Scholarship", "StudentProfile", "User", "University"]
