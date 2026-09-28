"""SQLAlchemy models for the application database."""

from sqlalchemy import String, ForeignKey, Float, DateTime, REAL, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from typing import Any

class Base(DeclarativeBase):
    """Base class for database models."""


class Camera(Base):
    """Store a camera's identity, type, and image dimensions."""

    __tablename__ = "cameras"

    camera_id: Mapped[str] = mapped_column(primary_key=True)
    camera_name: Mapped[str] = mapped_column(String)
    camera_type: Mapped[str] = mapped_column(String)
    width: Mapped[int] = mapped_column()
    height: Mapped[int] = mapped_column()

class Entity(Base): 
    __tablename__ = "entities"
    entity_id: Mapped[str] = mapped_column(primary_key=True)
    class_name: Mapped[str] = mapped_column(String)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attributes: Mapped[dict[str, Any]] = mapped_column(JSONB)

class Track(Base):
    __tablename__ = "tracks"
    track_id: Mapped[str] = mapped_column(primary_key=True)
    entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.entity_id")
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    confidence: Mapped[float] = mapped_column(Float)


class Event(Base):
    """Store camera events with timestamps and structured details."""

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    camera_id: Mapped[str | None] = mapped_column(
        ForeignKey("cameras.camera_id")
    )
    event_type: Mapped[str] = mapped_column(Text)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confidence: Mapped[float | None] = mapped_column(REAL)
    status: Mapped[str | None] = mapped_column(Text, server_default=text("'open'"))
    location_name: Mapped[str | None] = mapped_column(Text)
    structured_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )
    importance_score: Mapped[float | None] = mapped_column(
        REAL, server_default=text("0.5")
    )
