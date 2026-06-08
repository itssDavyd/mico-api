import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from dependencies import optional_auth
from routers.audio import router as audio_router
from routers.auth import router as auth_router
from routers.file import router as file_router
from routers.health import router as health_router
from services.job_store import close_redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    logger.info(
        "MICO API starting (stt=%s, ollama=%s/%s, auth=%s)",
        settings.stt_base_url or "local-whisper",
        settings.ollama_host,
        settings.ollama_model,
        settings.auth_enabled,
    )
    yield
    await close_redis()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="MICO API",
        description="Meeting Intelligence: audio → PDF document",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, tags=["Health"])
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(
        audio_router,
        prefix="/audio",
        tags=["Audio"],
        dependencies=[Depends(optional_auth)],
    )
    app.include_router(
        file_router,
        prefix="/file",
        tags=["File"],
        dependencies=[Depends(optional_auth)],
    )

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:create_app", host="0.0.0.0", port=8000, reload=True, factory=True)
