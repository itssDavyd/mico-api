import logging

from config import get_settings
from models.schemas import TranscriptionResult
from services.stt_client import transcribe_via_stt

logger = logging.getLogger(__name__)


def transcribe_audio(file_path: str) -> TranscriptionResult:
    settings = get_settings()

    if not settings.uses_remote_stt:
        raise RuntimeError(
            "STT_BASE_URL is not configured. MICO requires the remote thor-stt "
            "service for transcription."
        )

    return transcribe_via_stt(file_path)
