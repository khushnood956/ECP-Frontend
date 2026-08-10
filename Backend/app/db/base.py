import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    Shared Declarative Base for SQLAlchemy models.
    All models must inherit from this class.
    """

    # Generate __tablename__ automatically based on class name
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class UUIDPrimaryKeyMixin:
    """
    Mixin that provides a standard UUID primary key column.
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )


def _get_utc_now() -> datetime:
    """Returns a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """
    Mixin that provides timezone-aware created_at and updated_at columns.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_get_utc_now, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_get_utc_now,
        onupdate=_get_utc_now,
    )
