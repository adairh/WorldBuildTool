import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

def _load_base_settings() -> type:
    """Return the appropriate ``BaseSettings`` class for the installed stack."""

    try:  # Pydantic v2 location
        from pydantic_settings import BaseSettings as _BaseSettings

        return _BaseSettings
    except ImportError:  # pragma: no cover - fallback for Pydantic v1 environments
        from pydantic import BaseModel, __version__ as pydantic_version

        if pydantic_version.startswith("1."):
            from pydantic import BaseSettings as _BaseSettings  # type: ignore[assignment]

            return _BaseSettings

        class _CompatBaseSettings(BaseModel):
            """Very small shim mimicking ``BaseSettings`` for local execution."""

            model_config = {"extra": "ignore"}

            def __init__(self, **data: Any) -> None:  # type: ignore[override]
                env_values: Dict[str, Any] = {}
                config = getattr(self.__class__, "Config", None)
                env_file = getattr(config, "env_file", None)
                env_encoding = getattr(config, "env_file_encoding", "utf-8")

                if env_file:
                    self._load_env_file(env_file, env_encoding)

                for name in self.model_fields:
                    env_key = name.upper()
                    env_value = os.getenv(env_key)
                    if env_value is not None:
                        env_values[name] = env_value

                env_values.update(data)
                super().__init__(**env_values)

            @staticmethod
            def _load_env_file(path: str, encoding: str) -> None:
                try:
                    with open(path, "r", encoding=encoding) as handle:
                        for line in handle:
                            if not line or line.startswith("#"):
                                continue
                            if "=" not in line:
                                continue
                            key, value = line.strip().split("=", 1)
                            os.environ.setdefault(key, value)
                except FileNotFoundError:  # pragma: no cover - optional file
                    pass

        return _CompatBaseSettings


BaseSettings = _load_base_settings()


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
