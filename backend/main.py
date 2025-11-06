import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.audio import router as audio_router
from routers.file import router as file_router
from routers.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(title="MICO Backend")

    origins = os.getenv("FRONTEND_ORIGINS", "").split(",")
    origins = [origin.strip() for origin in origins if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registrar routers
    app.include_router(audio_router, prefix="/audio", tags=["Audio"])
    app.include_router(file_router, prefix="/file", tags=["File"])
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:create_app", host="0.0.0.0", port=8000, reload=True, factory=True)
