from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models.poi import POI
from ..schemas import POI as POISchema, WorldRequest
from ..services import generate_world

router = APIRouter(prefix="/pois", tags=["pois"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/preview", response_model=List[POISchema])
def preview_pois(
    seed: int = Query(42, description="Seed for deterministic POI generation"),
    households: int = Query(5, ge=1, le=32, description="Base household count for spatial synthesis"),
) -> List[POISchema]:
    request = WorldRequest(seed=seed, household_count=households, quest_count=2, event_count=4)
    bundle = generate_world(request)
    return bundle.pois


@router.get("/", response_model=List[dict])
def list_pois(db: Session = Depends(get_db)):
    pois = db.query(POI).all()
    return [
        {
            "id": poi.id,
            "name": poi.name,
            "geometry": poi.geometry,
            "layers": poi.layers,
            "tags": poi.tags,
            "description": poi.description,
        }
        for poi in pois
    ]
