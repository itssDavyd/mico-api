import redis.asyncio as redis
from datetime import UTC, datetime
from uuid import UUID

from models.schemas import JobRecord, JobStatus

JOB_KEY_PREFIX = "mico:job:"
JOB_TTL_SECONDS = 60 * 60 * 24 * 7


class JobStore:
    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    @staticmethod
    def _key(session_id: str | UUID) -> str:
        return f"{JOB_KEY_PREFIX}{session_id}"

    async def create_session(
        self,
        session_id: UUID,
        *,
        chunked: bool,
        original_filename: str = "recording.webm",
    ) -> JobRecord:
        record = JobRecord(
            id=session_id,
            status=JobStatus.UPLOADING if chunked else JobStatus.UPLOADED,
            progress_pct=0,
            stage="Awaiting audio" if chunked else "Queued",
            created_at=datetime.now(UTC),
            original_filename=original_filename,
            chunked=chunked,
        )
        await self.save(record)
        return record

    async def save(self, record: JobRecord) -> None:
        await self._client.setex(
            self._key(record.id),
            JOB_TTL_SECONDS,
            record.model_dump_json(),
        )

    async def get(self, session_id: str | UUID) -> JobRecord | None:
        raw = await self._client.get(self._key(session_id))
        if not raw:
            return None
        return JobRecord.model_validate_json(raw)

    async def update(
        self,
        session_id: str | UUID,
        **fields,
    ) -> JobRecord | None:
        record = await self.get(session_id)
        if not record:
            return None

        for key, value in fields.items():
            if value is not None and hasattr(record, key):
                setattr(record, key, value)

        await self.save(record)
        return record


_redis_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis_pool
    if _redis_pool is None:
        from config import get_settings

        _redis_pool = redis.from_url(get_settings().redis_url, decode_responses=True)
    return _redis_pool


async def get_job_store() -> JobStore:
    return JobStore(await get_redis())


async def close_redis() -> None:
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None
