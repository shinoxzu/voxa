import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models import MeetingStatus


class TranscriptSegment(BaseModel):
    start: float
    end: float
    speaker: str
    text: str


class TrackerIssue(BaseModel):
    key: str
    url: str


class ActionItem(BaseModel):
    id: int
    assignee: str
    task: str
    deadline: str | None = None
    tracker_issue: TrackerIssue | None = None


class ProcessingSteps(BaseModel):
    transcription: str = "pending"
    diarization: str = "pending"
    analysis: str = "pending"


class MeetingStatusResponse(BaseModel):
    status: MeetingStatus
    step: str | None = None
    steps: ProcessingSteps


class MeetingCreated(BaseModel):
    id: uuid.UUID
    status: MeetingStatus


class MeetingResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    status: MeetingStatus
    duration_sec: float | None = None
    transcript: list[TranscriptSegment] | None = None
    summary: str | None = None
    action_items: list[ActionItem] | None = None


class MeetingListItem(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    status: MeetingStatus
    duration_sec: float | None = None


class CreateIssueRequest(BaseModel):
    summary: str
    assignee: str | None = None
    deadline: str | None = None
    queue: str
