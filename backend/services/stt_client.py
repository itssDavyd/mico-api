import logging
import mimetypes
import os

import httpx

from config import get_settings
from models.schemas import TranscriptionResult

logger = logging.getLogger(__name__)


def transcribe_via_stt(file_path: str) -> TranscriptionResult:
    settings = get_settings()
    url = f"{settings.stt_base_url.rstrip('/')}{settings.stt_transcribe_path}"

    filename = os.path.basename(file_path) or "audio"
    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    with open(file_path, "rb") as audio_file:
        body = audio_file.read()

    if len(body) > settings.max_stt_audio_bytes:
        raise ValueError(
            f"Audio exceeds max_stt_audio_bytes ({settings.max_stt_audio_bytes} bytes)"
        )

    logger.info("Transcribing via thor-stt: %s", url)

    timeout = httpx.Timeout(settings.stt_timeout, connect=10.0)
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                url,
                files={"file": (filename, body, mime_type)},
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500] if exc.response is not None else str(exc)
        status = exc.response.status_code if exc.response is not None else None
        logger.warning("STT HTTP error status=%s body=%s", status, detail)
        raise RuntimeError(f"STT service error: {status}") from exc
    except httpx.RequestError as exc:
        logger.warning("STT request failed: %s", exc)
        raise RuntimeError("STT service unreachable") from exc

    data = response.json()
    text = str(data.get("text", "")).strip()

    return TranscriptionResult(text=text)
