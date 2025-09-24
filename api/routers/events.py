from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models.event import Event
from ..schemas import Event as EventSchema, WorldRequest
from ..services import generate_world

router = APIRouter(prefix="/events", tags=["events"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/preview", response_model=List[EventSchema])
def preview_events(
    seed: int = Query(42, description="Seed for deterministic timeline generation"),
    households: int = Query(6, ge=1, le=32),
    events: int = Query(8, ge=1, le=64),
) -> List[EventSchema]:
    request = WorldRequest(seed=seed, household_count=households, event_count=events, quest_count=3)
    bundle = generate_world(request)
    return bundle.events


@router.get("/", response_model=List[dict])
def list_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return [
        {
            "id": event.id,
            "date": event.date.isoformat() if event.date else None,
            "title": event.title,
            "description": event.description,
            "linkedPoiIds": event.linkedPoiIds,
            "linkedPersonIds": event.linkedPersonIds,
        }
        for event in events
    ]
