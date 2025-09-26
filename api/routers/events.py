from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import Event
from ..services import add_event, delete_event, get_world

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[Event])
def list_events() -> list[Event]:
    return list(get_world().events)


@router.post("", response_model=Event)
def create_event(event: Event) -> Event:
    return add_event(event)


@router.put("/{event_id}", response_model=Event)
def update_event(event_id: str, event: Event) -> Event:
    return add_event(event.model_copy(update={"id": event_id}))


@router.delete("/{event_id}", status_code=204)
def remove_event(event_id: str) -> None:
    if not next((item for item in get_world().events if item.id == event_id), None):
        raise HTTPException(status_code=404, detail="Event not found")
    delete_event(event_id)
