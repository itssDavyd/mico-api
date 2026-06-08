import logging

from arq import create_pool
from arq.connections import RedisSettings

from config import get_settings
from models.schemas import JobStatus
from services.job_store import JobStore

logger = logging.getLogger(__name__)


async def enqueue_job(job_name: str, *args: str) -> None:
    settings = get_settings()
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await redis.enqueue_job(job_name, *args)
    finally:
        await redis.aclose()


async def enqueue_or_fail(store: JobStore, session_id, job_name: str, *args: str) -> None:
    try:
        await enqueue_job(job_name, *args)
    except Exception as exc:
        logger.exception("Failed to enqueue %s for %s", job_name, session_id)
        await store.update(
            session_id,
            status=JobStatus.ERROR,
            error=f"Queue unavailable: {exc}",
        )
        raise
