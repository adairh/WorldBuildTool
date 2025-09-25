from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from ..models import Quest
from ..services import generate_quests
from ..storage import load_dataset

router = APIRouter(prefix="/quests", tags=["quests"])


@router.get("", response_model=List[Quest])
def list_quests() -> List[Quest]:
    return [Quest.model_validate(item) for item in load_dataset("quests", factory=list)]


@router.post("/generate", response_model=List[Quest])
def regenerate(payload: Dict[str, int] | None = None) -> List[Quest]:
    payload = payload or {}
    count = payload.get("count", 6)
    seed = payload.get("seed")
    return generate_quests(count=count, seed=seed)

