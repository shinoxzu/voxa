from abc import ABC, abstractmethod
from dataclasses import dataclass

import whisperx

from app.config import Settings


@dataclass
class Segment:
    start: float
    end: float
    text: str


class Transcriber(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> list[Segment]: ...


class WhisperXTranscriber(Transcriber):
    def __init__(self, settings: Settings) -> None:
        self._device = settings.whisper_device
        self._model = whisperx.load_model(
            settings.whisper_model,
            self._device,
            compute_type=settings.whisper_compute_type,
        )

    def transcribe(self, audio_path: str) -> list[Segment]:
        audio = whisperx.load_audio(audio_path)
        result = self._model.transcribe(audio, batch_size=4)

        language = result.get("language", "ru")
        align_model, metadata = whisperx.load_align_model(
            language_code=language, device=self._device
        )
        aligned = whisperx.align(
            result["segments"],
            align_model,
            metadata,
            audio,
            self._device,
            return_char_alignments=False,
        )

        return [
            Segment(start=seg["start"], end=seg["end"], text=seg["text"].strip())
            for seg in aligned["segments"]
        ]


class WhisperCppTranscriber(Transcriber):
    """Транскрайбер на whisper.cpp — поддерживает Metal (Mac) и CUDA через pywhispercpp."""

    def __init__(self, settings: Settings) -> None:
        from pywhispercpp.model import Model

        self._model = Model(
            settings.whisper_model,
            n_threads=4,
            print_progress=False,
            print_realtime=False,
        )

    def transcribe(self, audio_path: str) -> list[Segment]:
        # pywhispercpp по пути открывает только WAV — декодим любой формат через
        # ffmpeg в float32 16 кГц моно и передаём готовый numpy-массив.
        audio = whisperx.load_audio(audio_path)
        segments = self._model.transcribe(
            audio,
            language="ru",
            # анти-галлюцинационные пороги: на тишине/шуме whisper любит
            # дорисовывать "спасибо за просмотр" и т.п. — отсекаем по
            # вероятности речи и логлайкелихуду.
            no_speech_thold=0.6,
            logprob_thold=-1.0,
            suppress_nst=True,
        )   
        return [
            Segment(start=s.t0 / 100.0, end=s.t1 / 100.0, text=s.text.strip())
            for s in segments
        ]
