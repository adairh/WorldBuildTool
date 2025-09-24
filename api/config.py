from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseSettings


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
    for key, value in settings.dict().items():
        summary[key] = "***" if key in hidden_keys else value
    summary["storage_dir"] = str(Path(settings.storage_dir).expanduser())
    return summary
