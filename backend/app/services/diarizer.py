import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

import whisperx
from whisperx.diarize import DiarizationPipeline

from app.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class SpeakerSegment:
    start: float
    end: float
    speaker: str


class Diarizer(ABC):
    @abstractmethod
    def diarize(self, audio_path: str) -> list[SpeakerSegment]: ...


class PyAnnoteDiarizer(Diarizer):
    def __init__(self, settings: Settings) -> None:
        if settings.diarizer_device == "mps":
            os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
        logger.info("Creating pyannote pipeline on device=%s", settings.diarizer_device)
        self._pipeline = DiarizationPipeline(
            token=settings.hf_token, device=settings.diarizer_device
        )

    def diarize(self, audio_path: str) -> list[SpeakerSegment]:
        audio = whisperx.load_audio(audio_path)
        result = self._pipeline(audio)

        segments = []
        for _, row in result.iterrows():  # ty: ignore[unresolved-attribute]
            segments.append(
                SpeakerSegment(
                    start=row["start"],
                    end=row["end"],
                    speaker=row["speaker"],
                )
            )
        return segments
