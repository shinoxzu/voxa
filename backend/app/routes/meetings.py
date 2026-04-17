import asyncio
import uuid
from pathlib import Path

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from app.config import Settings
from app.dto import (
    ActionItem,
    CreateIssueRequest,
    MeetingCreated,
    MeetingListItem,
    MeetingResponse,
    MeetingStatusResponse,
    ProcessingSteps,
    TrackerIssue,
    TranscriptSegment,
)
from app.models import Meeting, MeetingStatus
from app.services.processor import MeetingProcessor
from app.services.tracker import Tracker

router = APIRouter(prefix="/meetings", tags=["meetings"], route_class=DishkaRoute)


@router.post("", status_code=201)
async def create_meeting(
    file: UploadFile,
    session: FromDishka[AsyncSession],
    processor: FromDishka[MeetingProcessor],
    settings: FromDishka[Settings],
    title: str = "Untitled",
) -> MeetingCreated:
    audio_dir = Path(settings.audio_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)

    meeting_id = uuid.uuid4()
    suffix = Path(file.filename or "audio.wav").suffix
    audio_path = audio_dir / f"{meeting_id}{suffix}"

    content = await file.read()
    audio_path.write_bytes(content)

    meeting = Meeting(
        id=meeting_id,
        title=title,
        audio_path=str(audio_path),
        status=MeetingStatus.processing,
        processing_step="transcription",
    )
    session.add(meeting)
    await session.commit()

    asyncio.create_task(processor.process(meeting_id))

    return MeetingCreated(id=meeting_id, status=MeetingStatus.processing)


@router.get("")
async def list_meetings(session: FromDishka[AsyncSession]) -> list[MeetingListItem]:
    result = await session.execute(select(Meeting).order_by(Meeting.created_at.desc()))
    meetings = result.scalars().all()
    return [
        MeetingListItem(
            id=m.id,
            title=m.title,
            created_at=m.created_at,
            status=m.status,
            duration_sec=m.duration_sec,
        )
        for m in meetings
    ]


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: uuid.UUID, session: FromDishka[AsyncSession]
) -> MeetingResponse:
    meeting = await session.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(404, "Meeting not found")

    transcript = None
    if meeting.transcript:
        transcript = [TranscriptSegment(**seg) for seg in meeting.transcript]

    action_items = None
    if meeting.action_items:
        action_items = [
            ActionItem(
                id=item["id"],
                assignee=item["assignee"],
                task=item["task"],
                deadline=item.get("deadline"),
                tracker_issue=(
                    TrackerIssue(**item["tracker_issue"])
                    if item.get("tracker_issue")
                    else None
                ),
            )
            for item in meeting.action_items
        ]

    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        created_at=meeting.created_at,
        status=meeting.status,
        duration_sec=meeting.duration_sec,
        transcript=transcript,
        summary=meeting.summary,
        action_items=action_items,
    )


@router.get("/{meeting_id}/status")
async def get_meeting_status(
    meeting_id: uuid.UUID, session: FromDishka[AsyncSession]
) -> MeetingStatusResponse:
    meeting = await session.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(404, "Meeting not found")

    step = meeting.processing_step
    steps = ProcessingSteps()

    if meeting.status == MeetingStatus.done:
        steps.transcription = "done"
        steps.diarization = "done"
        steps.analysis = "done"
    elif step == "transcription":
        steps.transcription = "running"
    elif step == "diarization":
        steps.transcription = "done"
        steps.diarization = "running"
    elif step == "analysis":
        steps.transcription = "done"
        steps.diarization = "done"
        steps.analysis = "running"

    return MeetingStatusResponse(status=meeting.status, step=step, steps=steps)


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(
    meeting_id: uuid.UUID, session: FromDishka[AsyncSession]
) -> None:
    meeting = await session.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(404, "Meeting not found")
    audio = Path(meeting.audio_path)
    if audio.exists():
        audio.unlink()
    await session.delete(meeting)
    await session.commit()


@router.post("/{meeting_id}/action-items/{item_id}/create-issue", status_code=201)
async def create_issue(
    meeting_id: uuid.UUID,
    item_id: int,
    body: CreateIssueRequest,
    session: FromDishka[AsyncSession],
    tracker: FromDishka[Tracker],
) -> TrackerIssue:
    meeting = await session.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(404, "Meeting not found")
    if not meeting.action_items or item_id >= len(meeting.action_items):
        raise HTTPException(404, "Action item not found")
    if meeting.action_items[item_id].get("tracker_issue"):
        raise HTTPException(409, "Issue already created")

    issue = await tracker.create_issue(
        queue=body.queue,
        summary=body.summary,
        assignee=body.assignee,
        deadline=body.deadline,
    )

    meeting.action_items[item_id]["tracker_issue"] = {
        "key": issue.key,
        "url": issue.url,
    }
    attributes.flag_modified(meeting, "action_items")
    await session.commit()

    return TrackerIssue(key=issue.key, url=issue.url)
