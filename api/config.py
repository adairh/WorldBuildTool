from __future__ import annotations

import os
from pathlib import Path
from pydantic import BaseModel, Field


class Settings(BaseModel):
    data_dir: Path = Field(default_factory=lambda: Path(os.getenv("TLFORGE_DATA_DIR", "data")))
    state_file: Path = Field(default_factory=lambda: Path(os.getenv("TLFORGE_STATE_FILE", "data/state.json")))
    memory_file: Path = Field(default_factory=lambda: Path(os.getenv("TLFORGE_MEMORY_FILE", "data/memory.json")))
    openai_api_key: str | None = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_base_url: str | None = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL"))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    generation_max_retries: int = Field(default=3, ge=1)

    class Config:
        frozen = True


def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    if not settings.state_file.exists():
        settings.state_file.write_text("{}", encoding="utf-8")
    if not settings.memory_file.exists():
        settings.memory_file.write_text("[]", encoding="utf-8")
    return settings
