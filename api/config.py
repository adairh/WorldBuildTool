from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    """Lightweight settings object for the file-backed toolkit."""

    storage_dir: Path = Path(os.getenv("STORAGE_DIR", "./storage")).expanduser()
    export_subdir: str = os.getenv("EXPORT_SUBDIR", "exports")
    memory_filename: str = os.getenv("CHAT_MEMORY_FILE", "chat_memory.json")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    max_memory_messages: int = int(os.getenv("CHAT_MEMORY_LIMIT", "24"))
    use_fake_ai: bool = os.getenv("TLFORGE_FAKE_AI", "0").lower() in {"1", "true", "yes"}

    model_config = ConfigDict(arbitrary_types_allowed=True)


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
        "memory_file": str(settings.storage_dir / settings.memory_filename),
        "openai_model": settings.openai_model,
        "ai_mode": "fake" if settings.use_fake_ai else "live",
    }
