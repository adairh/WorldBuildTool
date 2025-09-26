from __future__ import annotations

from typing import Dict

from fastapi import APIRouter

from ..config import settings_summary
from ..services import regenerate_foundation, validation_summary
from ..storage import load_dataset

router = APIRouter(prefix="/world", tags=["world"])


@router.post("/regenerate")
def regenerate(payload: Dict[str, int] | None = None) -> Dict[str, object]:
    seed = (payload or {}).get("seed", 42)
    snapshot = regenerate_foundation(seed=seed)
    return {"seed": seed, "datasets": {key: len(value) for key, value in snapshot.items()}}


@router.get("/dashboard")
def dashboard() -> Dict[str, object]:
    summary = validation_summary()
    summary["storage"] = settings_summary()
    summary_counts = summary.get("dataset_counts", {})
    summary["dataset_counts"] = {
        **summary_counts,
        "pois": len(load_dataset("pois", factory=list)),
        "households": len(load_dataset("households", factory=list)),
        "persons": len(load_dataset("persons", factory=list)),
        "events": len(load_dataset("events", factory=list)),
        "quests": len(load_dataset("quests", factory=list)),
        "story_arcs": len(load_dataset("story_arcs", factory=list)),
        "monster_zones": len(load_dataset("monster_zones", factory=list)),
        "features": len(load_dataset("features", factory=list)),
        "items": len(load_dataset("items", factory=list)),
        "activities": len(load_dataset("activities", factory=list)),
    }
    return summary

