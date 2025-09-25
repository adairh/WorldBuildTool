from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterable, MutableMapping, MutableSequence
from datetime import date, datetime

from .config import ensure_storage_dir, get_settings

DataLike = MutableMapping[str, Any] | MutableSequence[Any]


def dataset_path(name: str) -> Path:
    base = ensure_storage_dir()
    return base / f"{name}.json"


def load_dataset(name: str, factory: Callable[[], DataLike] | None = None) -> DataLike:
    path = dataset_path(name)
    if not path.exists():
        return factory() if factory else []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def save_dataset(name: str, data: DataLike) -> Path:
    path = dataset_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, default=_json_default)
    return path


def export_path(filename: str) -> Path:
    settings = get_settings()
    export_dir = settings.storage_dir / settings.export_subdir
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir / filename


def list_exports() -> Iterable[Path]:
    export_dir = get_settings().storage_dir / get_settings().export_subdir
    if not export_dir.exists():
        return []
    return sorted(export_dir.glob("*"))


def reset_storage() -> None:
    """Remove all JSON payloads (for tests)."""

    base = ensure_storage_dir()
    for path in base.glob("*.json"):
        path.unlink(missing_ok=True)
