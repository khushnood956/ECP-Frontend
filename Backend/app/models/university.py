from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class University(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Universities that students can browse.
    """

    __tablename__ = "universities"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    ranking: Mapped[str | None] = mapped_column(String(100), nullable=True)
    type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tuition_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    programs: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<University {self.name}>"
