from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable, Optional

from pydantic import ValidationError

from ..models import Asset, Event, Household, POI, Quest, WorldNote, WorldState
from ..storage import dataset_path, load_dataset, save_dataset

WORLD_DATASET = "world_state"
_MEDIA_DIR = "media"
_CACHE: Optional[WorldState] = None


class WorldStateError(RuntimeError):
    """Raised when a world operation fails."""


def _default_world() -> WorldState:
    return WorldState()


def _load_world() -> WorldState:
    payload = load_dataset(WORLD_DATASET, factory=lambda: _default_world().model_dump())
    try:
        return WorldState.model_validate(payload)
    except ValidationError as exc:
        raise WorldStateError(f"World data corrupted: {exc}")


def _store_world(world: WorldState) -> None:
    save_dataset(WORLD_DATASET, world.model_dump(mode="json"))


def get_world(refresh: bool = False) -> WorldState:
    global _CACHE
    if refresh or _CACHE is None:
        _CACHE = _load_world()
    return _CACHE


def update_world(mutator: Callable[[WorldState], None]) -> WorldState:
    world = get_world().model_copy(deep=True)
    mutator(world)
    _store_world(world)
    return get_world(refresh=True)


def list_pois() -> Iterable[POI]:
    return get_world().pois


def create_or_update_poi(poi: POI) -> POI:
    def mutate(world: WorldState) -> None:
        world.ensure_layer(poi.layer)
        existing = world.find_poi(poi.id)
        if existing:
            existing.name = poi.name
            existing.description = poi.description
            existing.layer = poi.layer
            existing.x = poi.x
            existing.y = poi.y
            existing.tags = poi.tags
            existing.media = poi.media
        else:
            world.pois.append(poi)

    update_world(mutate)
    return poi


def delete_poi(poi_id: str) -> None:
    def mutate(world: WorldState) -> None:
        world.pois = [poi for poi in world.pois if poi.id != poi_id]
        for household in world.households:
            if household.home_poi_id == poi_id:
                household.home_poi_id = None
        for quest in world.quests:
            for step in quest.steps:
                if step.poi_id == poi_id:
                    step.poi_id = None
        for event in world.events:
            if event.poi_id == poi_id:
                event.poi_id = None

    update_world(mutate)


def add_household(household: Household) -> Household:
    def mutate(world: WorldState) -> None:
        existing = world.find_household(household.id)
        if existing:
            existing.name = household.name
            existing.home_poi_id = household.home_poi_id
            existing.notes = household.notes
            existing.members = household.members
        else:
            world.households.append(household)

    update_world(mutate)
    return household


def delete_household(household_id: str) -> None:
    def mutate(world: WorldState) -> None:
        world.households = [hh for hh in world.households if hh.id != household_id]

    update_world(mutate)


def add_quest(quest: Quest) -> Quest:
    def mutate(world: WorldState) -> None:
        existing = world.find_quest(quest.id)
        if existing:
            existing.title = quest.title
            existing.synopsis = quest.synopsis
            existing.arc = quest.arc
            existing.recommended_level = quest.recommended_level
            existing.steps = quest.steps
        else:
            world.quests.append(quest)

    update_world(mutate)
    return quest


def delete_quest(quest_id: str) -> None:
    def mutate(world: WorldState) -> None:
        world.quests = [quest for quest in world.quests if quest.id != quest_id]

    update_world(mutate)


def add_event(event: Event) -> Event:
    def mutate(world: WorldState) -> None:
        existing = next((item for item in world.events if item.id == event.id), None)
        if existing:
            existing.title = event.title
            existing.date = event.date
            existing.description = event.description
            existing.poi_id = event.poi_id
            existing.tags = event.tags
        else:
            world.events.append(event)

    update_world(mutate)
    return event


def delete_event(event_id: str) -> None:
    def mutate(world: WorldState) -> None:
        world.events = [event for event in world.events if event.id != event_id]

    update_world(mutate)


def add_asset(asset: Asset) -> Asset:
    def mutate(world: WorldState) -> None:
        existing = next((item for item in world.assets if item.id == asset.id), None)
        if existing:
            existing.name = asset.name
            existing.kind = asset.kind
            existing.status = asset.status
            existing.owner = asset.owner
            existing.tags = asset.tags
            existing.notes = asset.notes
            existing.reference = asset.reference
        else:
            world.assets.append(asset)

    update_world(mutate)
    return asset


def delete_asset(asset_id: str) -> None:
    def mutate(world: WorldState) -> None:
        world.assets = [asset for asset in world.assets if asset.id != asset_id]

    update_world(mutate)


def add_note(note: WorldNote) -> WorldNote:
    def mutate(world: WorldState) -> None:
        existing = next((item for item in world.notes if item.id == note.id), None)
        if existing:
            existing.title = note.title
            existing.body = note.body
        else:
            world.notes.append(note)

    update_world(mutate)
    return note


def delete_note(note_id: str) -> None:
    def mutate(world: WorldState) -> None:
        world.notes = [note for note in world.notes if note.id != note_id]

    update_world(mutate)


def set_map_image(path: str, width: int | None = None, height: int | None = None) -> None:
    def mutate(world: WorldState) -> None:
        world.map.base_image = path
        if width:
            world.map.width = width
        if height:
            world.map.height = height

    update_world(mutate)


def media_directory() -> Path:
    path = dataset_path(_MEDIA_DIR)
    path.parent.mkdir(parents=True, exist_ok=True)
    media_dir = path.parent / _MEDIA_DIR
    media_dir.mkdir(parents=True, exist_ok=True)
    return media_dir


def register_media_file(filename: str, content: bytes) -> str:
    directory = media_directory()
    target = directory / filename
    counter = 1
    while target.exists():
        stem = target.stem
        suffix = target.suffix
        target = directory / f"{stem}_{counter}{suffix}"
        counter += 1
    target.write_bytes(content)
    return str(target.relative_to(directory.parent))


def world_summary() -> dict:
    world = get_world()
    npc_total = sum(len(household.members) for household in world.households)
    coverage = {
        layer.name: len([poi for poi in world.pois if poi.layer == layer.name])
        for layer in world.map.layers
    }
    return {
        "total_pois": len(world.pois),
        "total_households": len(world.households),
        "total_npcs": npc_total,
        "total_quests": len(world.quests),
        "total_events": len(world.events),
        "map_layers": len(world.map.layers),
        "coverage": coverage,
    }




def reset_world_cache() -> None:
    global _CACHE
    _CACHE = None

def export_world(path: Path | None = None) -> Path:
    world = get_world()
    payload = json.dumps(world.model_dump(mode="json"), ensure_ascii=False, indent=2)
    if path is None:
        path = dataset_path("world_export.json")
    path.write_text(payload, encoding="utf-8")
    return path
