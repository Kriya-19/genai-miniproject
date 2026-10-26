from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_URL = f"sqlite:///{(BACKEND_DIR / 'diagnosure.db').as_posix()}"


class Settings(BaseSettings):
    app_name: str = "DiagnoSure API"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"
    frontend_origin: str = "http://192.168.31.238:5173"
    passport_share_base_url: str = "http://192.168.31.238:8000"
    database_url: str = DEFAULT_DATABASE_URL
    jwt_secret_key: str = "change-me-in-development"
    jwt_access_token_expire_minutes: int = 30
    upload_dir: str = str(BACKEND_DIR / "uploads")
    max_upload_size_mb: int = 10
    maps_provider: str = ""
    maps_api_key: str = ""
    maps_tile_url: str = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    overpass_url: str = "https://overpass-api.de/api/interpreter"
    overpass_fallback_urls: str = "https://overpass.kumi.systems/api/interpreter,https://overpass.private.coffee/api/interpreter"
    nominatim_url: str = "https://nominatim.openstreetmap.org/search"
    overpass_cache_ttl_seconds: int = 300
    overpass_min_interval_seconds: float = 1.0
    jitsi_provider: str = "jitsi"
    jitsi_base_url: str = "https://meet.jit.si"
    notification_provider: str = "local"
    fcm_project_id: str = ""
    fcm_credentials_file: str = ""
    reminder_poll_interval_seconds: int = 60
    enable_reminder_scheduler: bool = True
    enable_demo_fixtures: bool = True

    model_config = SettingsConfigDict(env_file=(".env", "backend/.env"), extra="ignore")

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        if not path.is_absolute():
            path = BACKEND_DIR.parent / path
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
