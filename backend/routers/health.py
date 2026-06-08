import httpx
from fastapi import APIRouter

from config import get_settings
from services.job_store import get_redis

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "mico-api"}


@router.get("/health/ready")
async def readiness() -> dict[str, str | bool]:
    settings = get_settings()
    checks: dict[str, str | bool] = {
        "api": True,
        "redis": False,
        "ollama": False,
        "stt": "skipped",
    }

    try:
        redis = await get_redis()
        checks["redis"] = bool(await redis.ping())
    except Exception:
        checks["redis"] = False

    try:
        with httpx.Client(timeout=5) as client:
            response = client.get(f"{settings.ollama_host.rstrip('/')}/api/tags")
            checks["ollama"] = response.status_code == 200
    except Exception:
        checks["ollama"] = False

    if settings.uses_remote_stt:
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{settings.stt_base_url.rstrip('/')}/health")
                checks["stt"] = response.status_code == 200
        except Exception:
            checks["stt"] = False

    stt_ok = checks["stt"] is True or checks["stt"] == "skipped"
    ready = checks["redis"] and checks["ollama"] and stt_ok
    return {"status": "ready" if ready else "degraded", **checks}
