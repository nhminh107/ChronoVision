"""Pydantic data contracts for database records."""

from datetime import datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CameraContract(BaseModel):
    """Camera identity and image dimensions."""

    model_config = ConfigDict(from_attributes=True)

    camera_id: str
    camera_name: str
    camera_type: str
    width: int
    height: int


class EntityContract(BaseModel):
    """Detected entity and its observed attributes."""

    model_config = ConfigDict(from_attributes=True)

    entity_id: str
    class_name: str
    first_seen: time
    lass_seen: time
    attributes: dict[str, Any]


class TrackContract(BaseModel):
    """Tracking interval for an entity."""

    model_config = ConfigDict(from_attributes=True)

    track_id: str
    entity_id: str
    start_time: time
    end_time: time
    confidence: float


class EventContract(BaseModel):
    """Camera event with timestamps and structured details."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    start_time: datetime
    camera_id: str | None = None
    end_time: datetime | None = None
    confidence: float | None = None
    status: str | None = "open"
    location_name: str | None = None
    structured_data: dict[str, Any] | None = Field(default_factory=dict)
    importance_score: float | None = 0.5
