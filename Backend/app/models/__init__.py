"""
Import all models here so that Alembic and SQLAlchemy can discover them automatically via Base.metadata.
Order of imports doesn't matter for metadata, but it avoids circular dependencies inside the models themselves.
"""

from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.agency import Agency
from app.models.scholarship import Scholarship
from app.models.lead import Lead

# Expose models for easier imports elsewhere
__all__ = [
    "User",
    "StudentProfile",
    "Agency",
    "Scholarship",
    "Lead"
]
