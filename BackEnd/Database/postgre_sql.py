"""PostgreSQL persistence and queries returning Pydantic contracts."""

import os
from datetime import datetime
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from BackEnd.Contract.data_contracts import (
    CameraContract,
    EntityContract,
    EventContract,
    TrackContract,
)
from .sql_models import Base, Camera, Entity, Event, Track

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
_ModelT = TypeVar("_ModelT", bound=Base)

DATABASE_URL = os.getenv("DATABASE_URL")


class Postgre_Manager:
    """Manage database sessions, inserts, and record queries."""

    def __init__(
        self, echo: bool = False, database_url: str | None = None
    ) -> None:
        connection_url = database_url or DATABASE_URL
        if not connection_url:
            raise ValueError("DATABASE_URL is missing or empty.")
        if connection_url.startswith(("postgresql://", "postgres://")):
            connection_url = "postgresql+psycopg://" + connection_url.split(
                "://", 1
            )[1]
        self.engine: Engine = create_engine(
            connection_url,
            echo=echo,
            pool_pre_ping=True,
        )
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=Session,
            autoflush=False,
            expire_on_commit=False,
        )

    def init_db(self) -> None:
        """Create tables that do not already exist."""

        Base.metadata.create_all(bind=self.engine)

    @staticmethod
    def _persist(session: Session, record: _ModelT) -> _ModelT:
        """Commit one ORM record and return it with database values loaded."""

        try:
            session.add(record)
            session.commit()
            session.refresh(record)
        except SQLAlchemyError:
            session.rollback()
            raise
        return record

    def add_camera(self, data: CameraContract) -> CameraContract:
        """Insert a camera and return its saved values."""
        with self.session_factory() as session:
            record = self._persist(session, Camera(**data.model_dump()))
            return CameraContract.model_validate(record)

    def add_entity(self, data: EntityContract) -> EntityContract:
        """Insert an entity and return its saved values."""
        with self.session_factory() as session:
            record = self._persist(session, Entity(**data.model_dump()))
            return EntityContract.model_validate(record)

    def add_track(self, data: TrackContract) -> TrackContract:
        """Insert a track referencing an existing entity."""
        with self.session_factory() as session:
            record = self._persist(session, Track(**data.model_dump()))
            return TrackContract.model_validate(record)

    def update_track(self, track_id: str, seen_at: datetime) -> None:
        """Update a track and its entity with the latest observation time."""
        with self.session_factory.begin() as session:
            track = session.get(Track, track_id)
            if track is None:
                raise ValueError(f"Track not found: {track_id}")

            entity = session.get(Entity, track.entity_id)
            if entity is None:
                raise ValueError(f"Entity not found: {track.entity_id}")

            track.end_time = seen_at
            entity.last_seen = seen_at

    def add_event(self, data: EventContract) -> EventContract:
        """Insert an event, applying database defaults to omitted fields."""
        with self.session_factory() as session:
            record = self._persist(
                session, Event(**data.model_dump(exclude_unset=True))
            )
            return EventContract.model_validate(record)

    def select_camera(self, camera_id: str) -> CameraContract | None:
        """Return a camera by primary key, or None if it does not exist."""
        with self.session_factory() as session:
            record = session.get(Camera, camera_id)
            return CameraContract.model_validate(record) if record else None

    def select_entity(self, entity_id: str) -> EntityContract | None:
        """Return an entity by primary key, or None if it does not exist."""
        with self.session_factory() as session:
            record = session.get(Entity, entity_id)
            return EntityContract.model_validate(record) if record else None

    def select_track(self, track_id: str) -> TrackContract | None:
        """Return a track by primary key, or None if it does not exist."""
        with self.session_factory() as session:
            record = session.get(Track, track_id)
            return TrackContract.model_validate(record) if record else None

    def select_event(self, event_id: str) -> EventContract | None:
        """Return an event by primary key, or None if it does not exist."""
        with self.session_factory() as session:
            record = session.get(Event, event_id)
            return EventContract.model_validate(record) if record else None

    @staticmethod
    def _validate_pagination(limit: int, offset: int) -> None:
        """Reject invalid pagination values before querying the database."""
        if limit <= 0 or offset < 0:
            raise ValueError(
                "limit must be positive and offset must be non-negative."
            )

    def select_cameras(
        self, *, limit: int = 100, offset: int = 0
    ) -> list[CameraContract]:
        """Return cameras ordered by ID with pagination."""
        self._validate_pagination(limit, offset)
        query = (
            select(Camera).order_by(Camera.camera_id).limit(limit).offset(offset)
        )
        with self.session_factory() as session:
            return [
                CameraContract.model_validate(row)
                for row in session.scalars(query)
            ]

    def select_entities(
        self, *, class_name: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[EntityContract]:
        """Return entities, optionally filtering by class name."""
        self._validate_pagination(limit, offset)
        query = select(Entity)
        if class_name is not None:
            query = query.where(Entity.class_name == class_name)
        query = query.order_by(Entity.entity_id).limit(limit).offset(offset)
        with self.session_factory() as session:
            return [
                EntityContract.model_validate(row)
                for row in session.scalars(query)
            ]

    def select_tracks(
        self, *, entity_id: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[TrackContract]:
        """Return tracks, optionally filtering by entity ID."""
        self._validate_pagination(limit, offset)
        query = select(Track)
        if entity_id is not None:
            query = query.where(Track.entity_id == entity_id)
        query = query.order_by(Track.track_id).limit(limit).offset(offset)
        with self.session_factory() as session:
            return [
                TrackContract.model_validate(row)
                for row in session.scalars(query)
            ]

    def select_events(
        self,
        *,
        camera_id: str | None = None,
        event_type: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EventContract]:
        """Return events, optionally filtering by camera, type, and status."""
        self._validate_pagination(limit, offset)
        query = select(Event)
        if camera_id is not None:
            query = query.where(Event.camera_id == camera_id)
        if event_type is not None:
            query = query.where(Event.event_type == event_type)
        if status is not None:
            query = query.where(Event.status == status)
        query = (
            query.order_by(Event.start_time, Event.id).limit(limit).offset(offset)
        )
        with self.session_factory() as session:
            return [
                EventContract.model_validate(row)
                for row in session.scalars(query)
            ]
