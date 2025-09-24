"""Export helpers for packaging TL-Forge artifacts."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Iterable, Mapping, Optional, Union

from ..config import ensure_storage_dir
from ..schemas import WorldBundle


def _resolve_output_path(
    filename: Union[str, Path], directory: Optional[Union[str, Path]] = None
) -> Path:
    output = Path(filename)
    if not output.is_absolute():
        base_dir = Path(directory) if directory is not None else ensure_storage_dir()
        output = base_dir / output
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def export_data(
    data: Mapping[str, Iterable],
    filename: Union[str, Path] = "export.zip",
    directory: Optional[Union[str, Path]] = None,
) -> str:
    """Write arbitrary mapping payloads to a zip archive."""

    output = _resolve_output_path(filename, directory)
    with zipfile.ZipFile(output, "w") as zf:
        for key, value in data.items():
            zf.writestr(f"{key}.json", json.dumps(value, ensure_ascii=False, indent=2))
    return str(output)


def export_world_bundle(
    bundle: WorldBundle,
    filename: Union[str, Path] = "world_bundle.zip",
    directory: Optional[Union[str, Path]] = None,
) -> str:
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
    return export_data(data, filename=filename, directory=directory)


__all__ = ["export_data", "export_world_bundle"]
