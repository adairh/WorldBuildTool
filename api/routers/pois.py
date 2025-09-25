from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..models import POI
from ..services import generate_poi
from ..storage import load_dataset, save_dataset

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


def _load_poi_models() -> List[POI]:
    return [POI.model_validate(item) for item in load_dataset("pois", factory=list)]


def _save_poi_models(pois: List[POI]) -> None:
    save_dataset("pois", [poi.model_dump() for poi in pois])


@router.get("", response_model=List[POI])
async def list_pois() -> List[POI]:
    return _load_poi_models()


@router.get("/{poi_id}", response_model=POI)
async def get_poi(poi_id: str) -> POI:
    for poi in _load_poi_models():
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
    )
    if payload.media:
        pois = _load_poi_models()
        for idx, item in enumerate(pois):
            if item.id == poi.id:
                item.properties.media = payload.media
                pois[idx] = item
                _save_poi_models(pois)
                poi = item
                break
    return poi


@router.put("/{poi_id}", response_model=POI)
async def update_poi(poi_id: str, payload: POIUpdate) -> POI:
    pois = _load_poi_models()
    for idx, poi in enumerate(pois):
        if poi.id != poi_id:
            continue
        data = poi.model_dump()
        if payload.name is not None:
            data["properties"]["name"] = payload.name
        if payload.layers is not None:
            data["properties"]["layers"] = payload.layers
        if payload.tags is not None:
            data["properties"]["tags"] = payload.tags
        if payload.description is not None:
            data["properties"]["description"] = payload.description
        if payload.kind is not None:
            data["properties"]["kind"] = payload.kind
        if payload.media is not None:
            data["properties"]["media"] = payload.media
        if payload.coordinates is not None:
            data["geometry"]["coordinates"] = payload.coordinates
        updated = POI.model_validate(data)
        pois[idx] = updated
        _save_poi_models(pois)
        return updated
    raise HTTPException(status_code=404, detail="POI not found")
