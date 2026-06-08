import logging
import os
from uuid import UUID

from models.schemas import JobStatus
from services.job_store import JobStore, get_redis
from services.pdf_generator import generate_pdf
from services.session_storage import list_part_paths, remove_session
from services.summarize import summarize_text
from services.transcription import transcribe_audio

logger = logging.getLogger(__name__)


async def _update(store: JobStore, session_id: UUID, **fields) -> None:
    await store.update(session_id, **fields)


def _cleanup_file(path: str) -> None:
    try:
        if os.path.isfile(path):
            os.remove(path)
    except OSError as exc:
        logger.warning("Could not remove %s: %s", path, exc)


async def _run_pipeline(
    store: JobStore,
    session_id: UUID,
    original_filename: str,
    audio_paths: list[str],
) -> None:
    total = len(audio_paths)
    transcripts: list[str] = []

    await _update(
        store,
        session_id,
        status=JobStatus.TRANSCRIBING,
        progress_pct=5,
        stage="Transcribing",
        parts_total=total,
        parts_transcribed=0,
    )

    for index, path in enumerate(audio_paths, start=1):
        result = transcribe_audio(path)
        if result.text.strip():
            transcripts.append(result.text.strip())

        pct = 5 + int((index / total) * 55)
        await _update(
            store,
            session_id,
            progress_pct=pct,
            stage=f"Transcribing part {index}/{total}",
            parts_transcribed=index,
        )

    full_text = " ".join(transcripts).strip()
    if not full_text:
        raise ValueError("Transcription is empty")

    await _update(
        store,
        session_id,
        status=JobStatus.SUMMARIZING,
        progress_pct=65,
        stage="Summarizing",
    )

    summary = summarize_text(full_text)

    await _update(
        store,
        session_id,
        status=JobStatus.GENERATING_PDF,
        progress_pct=85,
        stage="Generating PDF",
    )

    pdf_filename = generate_pdf(
        process_id=session_id,
        original_filename=original_filename,
        summary=summary,
    )

    await _update(
        store,
        session_id,
        status=JobStatus.DONE,
        progress_pct=100,
        stage="Complete",
        pdf_filename=pdf_filename,
    )
    logger.info("Session %s completed: %s", session_id, pdf_filename)


async def process_audio_job(
    _ctx: dict,
    session_id: str,
    file_path: str,
    original_filename: str,
) -> None:
    sid = UUID(session_id)
    store = JobStore(await get_redis())

    try:
        await _run_pipeline(store, sid, original_filename, [file_path])
    except Exception as exc:
        logger.exception("Session %s failed", session_id)
        await _update(
            store,
            sid,
            status=JobStatus.ERROR,
            progress_pct=0,
            stage="Failed",
            error=str(exc),
        )
    finally:
        _cleanup_file(file_path)


async def process_session_job(_ctx: dict, session_id: str) -> None:
    sid = UUID(session_id)
    store = JobStore(await get_redis())
    record = await store.get(sid)

    if not record:
        logger.error("Session %s not found", session_id)
        return

    parts = list_part_paths(session_id)
    if not parts:
        await _update(
            store,
            sid,
            status=JobStatus.ERROR,
            error="No audio parts uploaded",
            stage="Failed",
        )
        return

    paths = [path for _, path in parts]

    try:
        await _run_pipeline(store, sid, record.original_filename, paths)
    except Exception as exc:
        logger.exception("Session %s failed", session_id)
        await _update(
            store,
            sid,
            status=JobStatus.ERROR,
            progress_pct=0,
            stage="Failed",
            error=str(exc),
        )
    finally:
        remove_session(session_id)
