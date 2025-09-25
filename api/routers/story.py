from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from ..models import Quest, StoryArc
from ..services import generate_quests, generate_story_arcs
from ..storage import load_dataset

router = APIRouter(prefix="/story", tags=["story"])


def _load_quests() -> List[Quest]:
    return [Quest.model_validate(item) for item in load_dataset("quests", factory=list)]


@router.get("/arcs", response_model=List[StoryArc])
def list_arcs() -> List[StoryArc]:
    return [StoryArc.model_validate(item) for item in load_dataset("story_arcs", factory=list)]


@router.post("/arcs/generate", response_model=List[StoryArc])
def regenerate_arcs(payload: Dict[str, int] | None = None) -> List[StoryArc]:
    payload = payload or {}
    seed = payload.get("seed")
    quests = _load_quests()
    if not quests:
        quests = generate_quests(count=6, seed=seed)
    arcs = generate_story_arcs(quests, seed=seed)
    return arcs

