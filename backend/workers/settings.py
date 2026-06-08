from arq.connections import RedisSettings

from config import get_settings
from workers.pipeline import process_audio_job, process_session_job


class WorkerSettings:
    functions = [process_audio_job, process_session_job]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    max_jobs = 1
    job_timeout = 60 * 60 * 6
    keep_result = 3600
