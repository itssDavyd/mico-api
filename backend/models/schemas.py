from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    GENERATING_PDF = "generating_pdf"
    DONE = "done"
    ERROR = "error"


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class TranscriptionResult(BaseModel):
    text: str
    segments: list[TranscriptSegment] = Field(default_factory=list)


class ActionItem(BaseModel):
    task: str
    responsible: str | None = None


class MeetingSummary(BaseModel):
    brief: str
    products_discussed: list[str] = Field(default_factory=list)
    customer_needs: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    key_points: list[str] = Field(default_factory=list)
    agreements: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)


class JobRecord(BaseModel):
    id: UUID
    status: JobStatus
    progress_pct: int = 0
    stage: str = ""
    created_at: datetime
    original_filename: str
    pdf_filename: str | None = None
    error: str | None = None
    chunked: bool = False
    parts_uploaded: int = 0
    parts_transcribed: int = 0
    parts_total: int = 0


class SessionResponse(BaseModel):
    session_id: str
    status: JobStatus


class PartResponse(BaseModel):
    session_id: str
    part_index: int
    parts_uploaded: int
    status: JobStatus


class ProcessResponse(BaseModel):
    session_id: str
    status: str


class StatusResponse(BaseModel):
    session_id: str
    status: JobStatus
    progress_pct: int
    stage: str
    parts_uploaded: int = 0
    parts_transcribed: int = 0
    parts_total: int = 0
    pdf_filename: str | None = None
    download_url: str | None = None
    error: str | None = None
