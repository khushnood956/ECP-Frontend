import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase, declared_attr


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
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        nullable=False,
    )


def _get_utc_now() -> datetime:
    """Returns a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """
    Mixin that provides timezone-aware created_at and updated_at columns.
    """
    created_at = Column(
        DateTime(timezone=True),
        default=_get_utc_now,
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=_get_utc_now,
        onupdate=_get_utc_now,
        nullable=False
    )
