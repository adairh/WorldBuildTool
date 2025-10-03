from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from threading import Lock
from typing import Iterable, List

from .config import get_settings
from .models import WorldState, empty_world


_MEMORY_LOCK = Lock()


def _parse_json_sequence(raw: str) -> List[dict]:
    raw = raw.strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except JSONDecodeError:
        decoder = json.JSONDecoder()
        index = 0
        items: List[dict] = []
        length = len(raw)
        while index < length:
            while index < length and raw[index].isspace():
                index += 1
            if index >= length:
                break
            try:
                obj, index = decoder.raw_decode(raw, index)
            except JSONDecodeError:
                break
            if isinstance(obj, list):
                for entry in obj:
                    if isinstance(entry, dict):
                        items.append(entry)
            elif isinstance(obj, dict):
                items.append(obj)
        return items
    else:
        if isinstance(data, list):
            return [entry for entry in data if isinstance(entry, dict)]
        if isinstance(data, dict):
            return [data]
        return []


def _read_json(path: Path) -> dict:
    if not path.exists() or path.read_text(encoding="utf-8").strip() == "":
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_world() -> WorldState:
    settings = get_settings()
    data = _read_json(settings.state_file)
    if not data:
        return empty_world()
    return WorldState.parse_obj(data)


def save_world(state: WorldState) -> WorldState:
    settings = get_settings()
    state.touch()
    _write_json(settings.state_file, json.loads(state.json()))
    return state


def append_memory(entry: dict) -> None:
    settings = get_settings()
    with _MEMORY_LOCK:
        raw = settings.memory_file.read_text(encoding="utf-8") if settings.memory_file.exists() else "[]"
        history: List[dict] = _parse_json_sequence(raw)
        history.append(entry)
        settings.memory_file.write_text(
            json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def load_memory(limit: int | None = None) -> List[dict]:
    settings = get_settings()
    with _MEMORY_LOCK:
        raw = settings.memory_file.read_text(encoding="utf-8") if settings.memory_file.exists() else "[]"
        history: List[dict] = _parse_json_sequence(raw)
    if limit is not None:
        return history[-limit:]
    return history


def clear_households(state: WorldState, area_ids: Iterable[str] | None = None) -> WorldState:
    if area_ids is None:
        state.households = []
    else:
        target = set(area_ids)
        state.households = [h for h in state.households if h.area_id not in target]
    return save_world(state)
