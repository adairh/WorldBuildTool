from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models.quest import Quest
from ..schemas import Quest as QuestSchema, WorldRequest
from ..services import generate_world

router = APIRouter(prefix="/quests", tags=["quests"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/preview", response_model=List[QuestSchema])
def preview_quests(
    seed: int = Query(42, description="Seed for deterministic quest crafting"),
    households: int = Query(6, ge=1, le=32),
    quests: int = Query(5, ge=1, le=32),
) -> List[QuestSchema]:
    request = WorldRequest(seed=seed, household_count=households, quest_count=quests, event_count=8)
    bundle = generate_world(request)
    return bundle.quests


@router.get("/", response_model=List[dict])
def list_quests(db: Session = Depends(get_db)):
    quests = db.query(Quest).all()
    return [
        {
            "id": quest.id,
            "title": quest.title,
            "description": quest.description,
            "dialogueTree": quest.dialogueTree,
            "relatedEventIds": quest.relatedEventIds,
        }
        for quest in quests
    ]
