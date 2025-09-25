from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from ..models import MonsterZone
from ..services import generate_monster_zones
from ..storage import load_dataset

router = APIRouter(prefix="/monsters", tags=["monsters"])


@router.get("/zones", response_model=List[MonsterZone])
def list_zones() -> List[MonsterZone]:
    return [MonsterZone.model_validate(item) for item in load_dataset("monster_zones", factory=list)]


@router.post("/zones/generate", response_model=List[MonsterZone])
def regenerate(payload: Dict[str, int] | None = None) -> List[MonsterZone]:
    seed = (payload or {}).get("seed")
    return generate_monster_zones(seed=seed)

