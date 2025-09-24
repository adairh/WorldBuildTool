from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./tlforge.db"
    jwt_secret: str = "changeme"
    storage_endpoint: str = "http://minio:9000"
    storage_bucket: str = "tlforge"
    storage_access_key: str = "admin"
    storage_secret_key: str = "password"
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def settings_summary() -> Dict[str, Any]:
    settings = get_settings()
    hidden_keys: List[str] = ["jwt_secret", "storage_secret_key"]
    summary: Dict[str, Optional[str]] = {}
    for key, value in settings.dict().items():
        summary[key] = "***" if key in hidden_keys else value
    return summary
