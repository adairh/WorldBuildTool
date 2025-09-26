from __future__ import annotations

from fastapi import APIRouter

from ..models import WorldState
from ..services import export_world, get_world, world_summary

router = APIRouter(prefix="/world", tags=["world"])


@router.get("", response_model=WorldState)
def fetch_world() -> WorldState:
    return get_world()


@router.get("/summary")
def get_summary() -> dict:
    return world_summary()


@router.post("/export")
def export_world_state() -> dict:
    path = export_world()
    return {"path": str(path)}
