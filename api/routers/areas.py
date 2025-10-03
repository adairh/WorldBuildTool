from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import Area, WorldState
from ..services.generation import GenerationError, generate_households_for_areas
from ..storage import clear_households, load_world, save_world

router = APIRouter()


def _find_index(area_id: str, state: WorldState) -> int:
    for idx, item in enumerate(state.areas):
        if item.id == area_id:
            return idx
    raise HTTPException(status_code=404, detail="Area not found")


@router.get("/")
def list_areas() -> list[Area]:
    state = load_world()
    return state.areas


@router.post("/", status_code=201)
def create_area(payload: Area) -> Area:
    state = load_world()
    state.areas.append(payload)
    save_world(state)
    return payload


@router.put("/{area_id}")
def update_area(area_id: str, payload: Area) -> Area:
    state = load_world()
    idx = _find_index(area_id, state)
    state.areas[idx] = payload.copy(update={"id": area_id})
    save_world(state)
    return state.areas[idx]


@router.delete("/{area_id}", status_code=204)
def delete_area(area_id: str) -> None:
    state = load_world()
    idx = _find_index(area_id, state)
    state.areas.pop(idx)
    clear_households(state, [area_id])


@router.post("/{area_id}/generate")
def generate_area(area_id: str) -> dict:
    state = load_world()
    _find_index(area_id, state)  # ensure exists
    try:
        state, results = generate_households_for_areas(state, [area_id])
    except GenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": results.get(area_id, "unknown")}


@router.post("/generate_all")
def generate_all() -> dict:
    state = load_world()
    area_ids = [area.id for area in state.areas if area.planned_households > 0]
    if not area_ids:
        raise HTTPException(status_code=400, detail="Không có khu vực nào để tạo hộ")
    state, results = generate_households_for_areas(state, area_ids)
    return {"status": results}
