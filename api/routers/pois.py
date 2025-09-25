from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..models import POI
from ..services import delete_poi as delete_poi_service
from ..services import generate_poi, list_pois as service_list_pois
from ..services import update_poi as update_poi_service

router = APIRouter(prefix="/pois", tags=["pois"])


class POICreate(BaseModel):
    name: str
    layers: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    coordinates: Optional[List[float]] = None
    kind: str = "landmark"
    description: str = ""
    media: List[str] = Field(default_factory=list)


class POIUpdate(BaseModel):
    name: Optional[str] = None
    layers: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    coordinates: Optional[List[float]] = None
    kind: Optional[str] = None
    description: Optional[str] = None
    media: Optional[List[str]] = None


@router.get("", response_model=List[POI])
async def list_pois() -> List[POI]:
    return service_list_pois()


@router.get("/{poi_id}", response_model=POI)
async def get_poi(poi_id: str) -> POI:
    for poi in service_list_pois():
        if poi.id == poi_id:
            return poi
    raise HTTPException(status_code=404, detail="POI not found")


@router.post("", response_model=POI)
async def create_poi(payload: POICreate) -> POI:
    poi = generate_poi(
        payload.name,
        layers=payload.layers,
        tags=payload.tags,
        coordinates=payload.coordinates,
        description=payload.description,
        kind=payload.kind,
        media=payload.media,
    )
    return poi


@router.put("/{poi_id}", response_model=POI)
async def update_poi(poi_id: str, payload: POIUpdate) -> POI:
    try:
        return update_poi_service(
            poi_id,
            name=payload.name,
            layers=payload.layers,
            tags=payload.tags,
            description=payload.description,
            kind=payload.kind,
            media=payload.media,
            coordinates=payload.coordinates,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{poi_id}", status_code=204)
async def delete_poi(poi_id: str) -> None:
    try:
        delete_poi_service(poi_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
