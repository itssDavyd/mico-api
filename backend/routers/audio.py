import logging
import os
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from config import get_settings
from models.schemas import (
    JobStatus,
    PartResponse,
    ProcessResponse,
    SessionResponse,
    StatusResponse,
)
from services.job_store import get_job_store
from services.queue import enqueue_or_fail
from services.session_storage import count_parts, save_part

logger = logging.getLogger(__name__)
router = APIRouter()


def _parse_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid session_id") from exc


def _validate_audio(filename: str, size_bytes: int, *, is_chunk: bool) -> None:
    settings = get_settings()
    ext = Path(filename).suffix.lower()

    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(sorted(settings.allowed_extensions))}",
        )

    limit_mb = settings.max_chunk_mb if is_chunk else settings.max_upload_mb
    max_bytes = limit_mb * 1024 * 1024

    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {limit_mb} MB per {'chunk' if is_chunk else 'upload'}",
        )

    if settings.uses_remote_stt and size_bytes > settings.max_stt_audio_bytes:
        max_mb = settings.max_stt_audio_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"Chunk exceeds STT limit ({max_mb:.0f} MB)",
        )


def _status_response(record, request: Request) -> StatusResponse:
    download_url = None
    if record.pdf_filename:
        base = str(request.base_url).rstrip("/")
        download_url = f"{base}/file/download/{record.pdf_filename}"

    return StatusResponse(
        session_id=str(record.id),
        status=record.status,
        progress_pct=record.progress_pct,
        stage=record.stage,
        parts_uploaded=record.parts_uploaded,
        parts_transcribed=record.parts_transcribed,
        parts_total=record.parts_total,
        pdf_filename=record.pdf_filename,
        download_url=download_url,
        error=record.error,
    )


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    filename: str = Form(default="recording.webm"),
) -> SessionResponse:
    settings = get_settings()
    os.makedirs(settings.audio_dir, exist_ok=True)

    session_id = uuid4()
    safe_name = Path(filename).name

    store = await get_job_store()
    record = await store.create_session(session_id, chunked=True, original_filename=safe_name)

    return SessionResponse(session_id=str(record.id), status=record.status)


@router.post("/sessions/{session_id}/parts", response_model=PartResponse)
async def upload_part(
    session_id: str,
    part_index: int = Form(..., ge=0),
    file: UploadFile = File(...),
) -> PartResponse:
    sid = _parse_uuid(session_id)
    store = await get_job_store()
    record = await store.get(sid)

    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    if not record.chunked:
        raise HTTPException(status_code=400, detail="Session is not chunked")
    if record.status != JobStatus.UPLOADING:
        raise HTTPException(status_code=409, detail="Session is not accepting parts")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    content = await file.read()
    _validate_audio(file.filename, len(content), is_chunk=True)

    save_part(str(sid), part_index, file.filename, content)
    parts_uploaded = count_parts(str(sid))

    await store.update(
        sid,
        parts_uploaded=parts_uploaded,
        stage=f"Received {parts_uploaded} part(s)",
    )

    return PartResponse(
        session_id=str(sid),
        part_index=part_index,
        parts_uploaded=parts_uploaded,
        status=JobStatus.UPLOADING,
    )


@router.post("/sessions/{session_id}/finalize", response_model=ProcessResponse)
async def finalize_session(session_id: str) -> ProcessResponse:
    sid = _parse_uuid(session_id)
    store = await get_job_store()
    record = await store.get(sid)

    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    if record.status != JobStatus.UPLOADING:
        raise HTTPException(status_code=409, detail="Session already finalized")

    parts_uploaded = count_parts(str(sid))
    if parts_uploaded == 0:
        raise HTTPException(status_code=400, detail="No parts uploaded")

    await store.update(
        sid,
        status=JobStatus.UPLOADED,
        parts_uploaded=parts_uploaded,
        parts_total=parts_uploaded,
        stage="Queued",
        progress_pct=0,
    )

    try:
        await enqueue_or_fail(store, sid, "process_session_job", str(sid))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Queue unavailable") from exc

    return ProcessResponse(session_id=str(sid), status="processing")


@router.post("/process", response_model=ProcessResponse)
async def process_audio(file: UploadFile = File(...)) -> ProcessResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    content = await file.read()
    _validate_audio(file.filename, len(content), is_chunk=False)

    settings = get_settings()
    os.makedirs(settings.audio_dir, exist_ok=True)

    session_id = uuid4()
    safe_name = Path(file.filename).name
    file_path = os.path.join(settings.audio_dir, f"{session_id}_{safe_name}")

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    store = await get_job_store()
    await store.create_session(session_id, chunked=False, original_filename=safe_name)

    try:
        await enqueue_or_fail(
            store,
            session_id,
            "process_audio_job",
            str(session_id),
            file_path,
            safe_name,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Queue unavailable") from exc

    return ProcessResponse(session_id=str(session_id), status="processing")


@router.get("/status/{session_id}", response_model=StatusResponse)
async def get_status(session_id: str, request: Request) -> StatusResponse:
    sid = _parse_uuid(session_id)
    store = await get_job_store()
    record = await store.get(sid)

    if not record:
        raise HTTPException(status_code=404, detail="Session not found")

    return _status_response(record, request)
