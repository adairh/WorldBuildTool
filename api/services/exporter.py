from __future__ import annotations

import csv
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

from ..storage import export_path, load_dataset

SUPPORTED_FORMATS = {"json", "csv", "unity"}


def _timestamped_filename(prefix: str, extension: str) -> str:
    now = datetime.now(timezone.utc)
    return f"{prefix}-{now.strftime('%Y%m%d-%H%M%S')}.{extension}"


def _entry_key(entry: Dict[str, object], fallback_prefix: str, idx: int) -> str:
    for key in ("id", "person_id", "household_id", "event_id", "quest_id"):
        value = entry.get(key)
        if isinstance(value, str) and value:
            return value
    return f"{fallback_prefix}-{idx:04d}"


def export_bundle(types: Iterable[str], fmt: str = "json") -> Path:
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported export format: {fmt}")

    payload: Dict[str, List[Dict[str, object]]] = {}
    for item_type in types:
        data = load_dataset(item_type, factory=list)
        payload[item_type] = list(data)

    if fmt == "json":
        filename = _timestamped_filename("bundle", "json")
        path = export_path(filename)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        return path

    if fmt == "unity":
        filename = _timestamped_filename("bundle-unity", "json")
        path = export_path(filename)
        unity_payload = {
            key: {
                _entry_key(entry, key, idx): entry for idx, entry in enumerate(value)
            }
            for key, value in payload.items()
        }
        with path.open("w", encoding="utf-8") as handle:
            json.dump(unity_payload, handle, ensure_ascii=False, indent=2)
        return path

    base_dir = export_path(_timestamped_filename("csv", "dir").replace(".dir", ""))
    base_dir.mkdir(parents=True, exist_ok=True)
    for key, value in payload.items():
        if not value:
            continue
        headers = sorted({field for entry in value for field in entry.keys()})
        csv_path = base_dir / f"{key}.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            for entry in value:
                writer.writerow(entry)
    return base_dir


def list_available_exports() -> List[Path]:
    base = export_path("").parent
    if not base.exists():
        return []
    return sorted(base.glob("*"))
