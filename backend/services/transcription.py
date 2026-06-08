import logging
import threading

from config import get_settings
from models.schemas import TranscriptSegment, TranscriptionResult
from services.stt_client import transcribe_via_stt

logger = logging.getLogger(__name__)


class LocalTranscriptionService:
    _instance: "LocalTranscriptionService | None" = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._model = None
        self._model_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "LocalTranscriptionService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _ensure_model(self):
        if self._model is not None:
            return self._model

        with self._model_lock:
            if self._model is not None:
                return self._model

            from faster_whisper import WhisperModel

            settings = get_settings()
            logger.info(
                "Loading local Whisper model=%s device=%s compute_type=%s",
                settings.whisper_model,
                settings.resolved_whisper_device,
                settings.resolved_compute_type,
            )
            self._model = WhisperModel(
                settings.whisper_model,
                device=settings.resolved_whisper_device,
                compute_type=settings.resolved_compute_type,
            )
            return self._model

    def transcribe(self, file_path: str) -> TranscriptionResult:
        settings = get_settings()
        model = self._ensure_model()

        segments_iter, _info = model.transcribe(
            file_path,
            language=settings.whisper_language,
            vad_filter=True,
            beam_size=5,
        )

        segments: list[TranscriptSegment] = []
        text_parts: list[str] = []

        for segment in segments_iter:
            cleaned = segment.text.strip()
            if not cleaned:
                continue
            text_parts.append(cleaned)
            segments.append(
                TranscriptSegment(
                    start=segment.start,
                    end=segment.end,
                    text=cleaned,
                )
            )

        return TranscriptionResult(
            text=" ".join(text_parts).strip(),
            segments=segments,
        )


def transcribe_audio(file_path: str) -> TranscriptionResult:
    settings = get_settings()

    if settings.uses_remote_stt:
        return transcribe_via_stt(file_path)

    logger.info("STT_BASE_URL not set — using local faster-whisper")
    return LocalTranscriptionService.get_instance().transcribe(file_path)
