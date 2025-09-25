from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from ..models import GameplayFeature, Item, MonsterZone, Quest
from ..services import generate_items
from ..storage import load_dataset

router = APIRouter(prefix="/items", tags=["items"])


def _load_quests() -> List[Quest]:
    return [Quest.model_validate(item) for item in load_dataset("quests", factory=list)]


def _load_zones() -> List[MonsterZone]:
    return [MonsterZone.model_validate(item) for item in load_dataset("monster_zones", factory=list)]


def _load_features() -> List[GameplayFeature]:
    return [GameplayFeature.model_validate(item) for item in load_dataset("features", factory=list)]


@router.get("", response_model=List[Item])
def list_items() -> List[Item]:
    return [Item.model_validate(item) for item in load_dataset("items", factory=list)]


@router.post("/generate", response_model=List[Item])
def regenerate(payload: Dict[str, int] | None = None) -> List[Item]:
    seed = (payload or {}).get("seed")
    quests = _load_quests()
    zones = _load_zones()
    features = _load_features()
    return generate_items(quests, zones, features, seed=seed)

