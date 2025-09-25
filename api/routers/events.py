from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..models import Event
from ..services import generate_timeline
from ..storage import load_dataset, save_dataset

router = APIRouter(prefix="/events", tags=["events"])


class EventCreate(BaseModel):
    date: date
    title: str
    description: str = ""
    linked_poi_ids: List[str] = Field(default_factory=list)
    linked_person_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class EventGenerateRequest(BaseModel):
    days: int = Field(default=10, ge=1, le=120)
    seed: Optional[int] = None


def _load_events() -> List[Event]:
    return [Event.model_validate(item) for item in load_dataset("events", factory=list)]


def _save_events(events: List[Event]) -> None:
    save_dataset("events", [event.model_dump() for event in events])


@router.get("", response_model=List[Event])
async def list_events() -> List[Event]:
    return _load_events()


@router.post("", response_model=Event)
async def create_event(payload: EventCreate) -> Event:
    events = _load_events()
    event = Event(
        event_id=f"EV-{uuid4().hex[:6].upper()}",
        date=payload.date,
        title=payload.title,
        description=payload.description,
        linked_poi_ids=payload.linked_poi_ids,
        linked_person_ids=payload.linked_person_ids,
        tags=payload.tags,
    )
    events.append(event)
    _save_events(events)
    return event


@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: str) -> Event:
    for event in _load_events():
        if event.event_id == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")


@router.post("/generate", response_model=List[Event])
async def generate_events(request: EventGenerateRequest) -> List[Event]:
    return generate_timeline(request.days, seed=request.seed)
