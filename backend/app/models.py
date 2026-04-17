import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MeetingStatus(str, enum.Enum):
    processing = "processing"
    done = "done"
    error = "error"


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[MeetingStatus] = mapped_column(
        Enum(MeetingStatus), default=MeetingStatus.processing
    )
    processing_step: Mapped[str | None] = mapped_column(String(50), nullable=True)
    audio_path: Mapped[str] = mapped_column(String(500))
    duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    transcript: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_items: Mapped[list | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
