from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict

from pydantic import BaseModel


class Settings(BaseModel):
    """Lightweight settings object for the file-backed toolkit."""

    storage_dir: Path = Path(os.getenv("STORAGE_DIR", "./storage")).expanduser()
    export_subdir: str = os.getenv("EXPORT_SUBDIR", "exports")

    class Config:
        arbitrary_types_allowed = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def ensure_storage_dir() -> Path:
    settings = get_settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    export_dir = settings.storage_dir / settings.export_subdir
    export_dir.mkdir(parents=True, exist_ok=True)
    return settings.storage_dir


def settings_summary() -> Dict[str, str]:
    settings = get_settings()
    return {
        "storage_dir": str(settings.storage_dir),
        "export_dir": str(settings.storage_dir / settings.export_subdir),
    }
