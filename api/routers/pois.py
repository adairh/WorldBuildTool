from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import POI
from ..services import create_or_update_poi, delete_poi, get_world

router = APIRouter(prefix="/pois", tags=["pois"])


@router.get("", response_model=list[POI])
def list_pois_route() -> list[POI]:
    return list(get_world().pois)


@router.get("/{poi_id}", response_model=POI)
def get_poi(poi_id: str) -> POI:
    poi = get_world().find_poi(poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    return poi


@router.post("", response_model=POI)
def create_poi(poi: POI) -> POI:
    return create_or_update_poi(poi)


@router.put("/{poi_id}", response_model=POI)
def update_poi(poi_id: str, patch: POI) -> POI:
    patched = patch.model_copy(update={"id": poi_id})
    return create_or_update_poi(patched)


@router.delete("/{poi_id}", status_code=204)
def remove_poi(poi_id: str) -> None:
    delete_poi(poi_id)
