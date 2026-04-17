import asyncio
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import Meeting, MeetingStatus
from app.services.analyzer import Analyzer, DiarizedSegment
from app.services.diarizer import Diarizer
from app.services.transcriber import Transcriber

logger = logging.getLogger(__name__)


class MeetingProcessor:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        transcriber: Transcriber,
        diarizer: Diarizer,
        analyzer: Analyzer,
    ) -> None:
        self._session_factory = session_factory
        self._transcriber = transcriber
        self._diarizer = diarizer
        self._analyzer = analyzer

    async def process(self, meeting_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            meeting = await session.get(Meeting, meeting_id)
            if meeting is None:
                return
            await self._run(meeting, session)

    async def _run(self, meeting: Meeting, session: AsyncSession) -> None:
        try:
            meeting.processing_step = "transcription"
            await self._save(session, meeting)

            transcript_segments = await asyncio.to_thread(
                self._transcriber.transcribe, meeting.audio_path
            )

            meeting.processing_step = "diarization"
            await self._save(session, meeting)

            diarize_segments = await asyncio.to_thread(
                self._diarizer.diarize, meeting.audio_path
            )

            merged = self._merge(transcript_segments, diarize_segments)

            meeting.transcript = [  # ty: ignore[invalid-assignment]
                {
                    "start": s.start,
                    "end": s.end,
                    "speaker": s.speaker,
                    "text": s.text,
                }
                for s in merged
            ]

            meeting.processing_step = "analysis"
            await self._save(session, meeting)

            analysis = await self._analyzer.analyze(merged)

            meeting.summary = analysis.summary
            meeting.action_items = [
                {
                    "id": i,
                    "assignee": item.assignee,
                    "task": item.task,
                    "deadline": item.deadline,
                    "tracker_issue": None,
                }
                for i, item in enumerate(analysis.action_items)
            ]

            meeting.status = MeetingStatus.done
            meeting.processing_step = None

        except Exception as exc:
            logger.exception("Failed to process meeting %s", meeting.id)
            meeting.status = MeetingStatus.error
            meeting.error_message = f"{type(exc).__name__}: {exc}"

        await self._save(session, meeting)

    @staticmethod
    def _merge(
        transcript_segments: list, diarize_segments: list
    ) -> list[DiarizedSegment]:
        result = []
        for tseg in transcript_segments:
            best_speaker = "???"
            best_overlap = 0.0

            for dseg in diarize_segments:
                overlap_start = max(tseg.start, dseg.start)
                overlap_end = min(tseg.end, dseg.end)
                overlap = max(0.0, overlap_end - overlap_start)

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_speaker = dseg.speaker

            result.append(
                DiarizedSegment(
                    start=tseg.start,
                    end=tseg.end,
                    speaker=best_speaker,
                    text=tseg.text,
                )
            )
        return result

    @staticmethod
    async def _save(session: AsyncSession, meeting: Meeting) -> None:
        session.add(meeting)
        await session.commit()
