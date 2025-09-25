from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

try:  # Pydantic v2 location
    from pydantic_settings import BaseSettings
except ImportError:  # pragma: no cover - fallback for Pydantic v1 environments
    from pydantic import BaseSettings  # type: ignore[assignment]


class Settings(BaseSettings):
    database_url: str = "sqlite:///./tlforge.db"
    jwt_secret: str = "changeme"
    storage_dir: str = "./storage"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def ensure_storage_dir() -> Path:
    """Create the configured storage directory if missing."""

    settings = get_settings()
    storage_path = Path(settings.storage_dir).expanduser()
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def settings_summary() -> Dict[str, Any]:
    settings = get_settings()
    hidden_keys = {"jwt_secret"}
    summary: Dict[str, Optional[str]] = {}
    if hasattr(settings, "model_dump"):
        raw_settings = settings.model_dump()
    else:  # pragma: no cover - Pydantic v1 compatibility
        raw_settings = settings.dict()

    for key, value in raw_settings.items():
        summary[key] = "***" if key in hidden_keys else value
    summary["storage_dir"] = str(Path(settings.storage_dir).expanduser())
    return summary
