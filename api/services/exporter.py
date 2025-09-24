"""Export helpers for packaging TL-Forge artifacts."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Iterable, Mapping

from ..schemas import WorldBundle


def export_data(data: Mapping[str, Iterable], filename: str = "export.zip") -> str:
    """Write arbitrary mapping payloads to a zip archive."""

    output = Path(filename)
    with zipfile.ZipFile(output, "w") as zf:
        for key, value in data.items():
            zf.writestr(f"{key}.json", json.dumps(value, ensure_ascii=False, indent=2))
    return str(output)


def export_world_bundle(bundle: WorldBundle, filename: str = "world_bundle.zip") -> str:
    """Serialize a :class:`WorldBundle` into a structured archive."""

    payload = bundle.dict() if hasattr(bundle, "dict") else bundle.model_dump()
    manifest = {
        "seed": bundle.seed,
        "households": len(bundle.households),
        "persons": len(bundle.persons),
        "events": len(bundle.events),
        "quests": len(bundle.quests),
        "assets": len(bundle.assets),
    }
    data = {"manifest": manifest}
    data.update({k: v for k, v in payload.items() if k != "seed"})
    return export_data(data, filename=filename)


__all__ = ["export_data", "export_world_bundle"]
