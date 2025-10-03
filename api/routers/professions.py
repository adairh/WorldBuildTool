from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import Profession, WorldState
from ..storage import load_world, save_world

router = APIRouter()


def _find_index(profession_id: str, state: WorldState) -> int:
    for idx, item in enumerate(state.professions):
        if item.id == profession_id:
            return idx
    raise HTTPException(status_code=404, detail="Profession not found")


@router.get("/")
def list_professions() -> list[Profession]:
    state = load_world()
    return state.professions


@router.post("/", status_code=201)
def create_profession(payload: Profession) -> Profession:
    state = load_world()
    state.professions.append(payload)
    save_world(state)
    return payload


@router.put("/{profession_id}")
def update_profession(profession_id: str, payload: Profession) -> Profession:
    state = load_world()
    idx = _find_index(profession_id, state)
    state.professions[idx] = payload.copy(update={"id": profession_id})
    save_world(state)
    return state.professions[idx]


@router.delete("/{profession_id}", status_code=204)
def delete_profession(profession_id: str) -> None:
    state = load_world()
    idx = _find_index(profession_id, state)
    state.professions.pop(idx)
    save_world(state)
