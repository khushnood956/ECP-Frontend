"""
Import all models here so that Alembic and SQLAlchemy can discover them automatically via Base.metadata.
Order of imports doesn't matter for metadata, but it avoids circular dependencies inside the models themselves.
"""

from app.models.academic_class import Class
from app.models.agency import Agency
from app.models.application import ScholarshipApplicationRequirement, StudentApplicationResponse
from app.models.attendance import Attendance
from app.models.bookmark import Bookmark
from app.models.document import Document
from app.models.enrollment import Enrollment
from app.models.lead import Lead
from app.models.notification import Notification
from app.models.scholarship import Scholarship
from app.models.student_profile import StudentProfile
from app.models.university import University
from app.models.user import User

# Expose models for easier imports elsewhere
__all__ = [
    "Agency",
    "Attendance",
    "Bookmark",
    "Class",
    "Document",
    "Enrollment",
    "Lead",
    "Notification",
    "Scholarship",
    "StudentProfile",
    "University",
    "User"
]
