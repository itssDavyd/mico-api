from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_ENV = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ROOT_ENV if _ROOT_ENV.exists() else ".env",
        extra="ignore",
        populate_by_name=True,
    )

    frontend_origins: str = ""
    audio_dir: str = "./audio"
    pdf_dir: str = "./pdfs"
    redis_url: str = "redis://redis:6379"

    stt_base_url: str = ""
    stt_transcribe_path: str = "/transcribe"
    stt_timeout: int = Field(default=14_400, alias="STT_TIMEOUT_SECONDS")
    max_stt_audio_bytes: int = Field(default=200_000_000, alias="MAX_AUDIO_BYTES")

    ollama_host: str = "http://ollama:11434"
    ollama_model: str = "qwen2.5:7b-instruct-q4_K_M"
    ollama_timeout: int = Field(default=3600, alias="OLLAMA_TIMEOUT")
    ollama_chunk_chars: int = 6000
    ollama_temperature: float = 0.1
    ollama_num_predict: int = 2048

    max_upload_mb: int = Field(default=200, alias="MAX_UPLOAD_MB")
    max_chunk_mb: int = Field(default=50, alias="MAX_CHUNK_MB")
    allowed_audio_extensions: str = ".wav,.mp3,.m4a,.webm,.ogg,.flac,.mp4"

    session_token: str = Field(default="changeme", alias="SESSION_TOKEN")
    first_username: str = Field(default="admin", alias="FIRST_USERNAME")
    first_password: str = Field(default="changeme", alias="FIRST_PASWORD")
    auth_enabled: bool = Field(default=True, alias="AUTH_ENABLED")
    # Session cookie ``Secure`` flag. Keep True when serving over HTTPS (Thor prod).
    cookie_secure: bool = Field(default=True, alias="COOKIE_SECURE")

    @property
    def uses_remote_stt(self) -> bool:
        return bool(self.stt_base_url.strip())

    @property
    def cors_origins(self) -> list[str]:
        origins = [o.strip() for o in self.frontend_origins.split(",") if o.strip()]
        return origins if origins else ["*"]

    @property
    def allowed_extensions(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_audio_extensions.split(",")}


@lru_cache
def get_settings() -> Settings:
    return Settings()
