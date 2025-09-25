from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from ..models import Activity
from ..services import generate_activities
from ..storage import load_dataset

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=List[Activity])
def list_activities() -> List[Activity]:
    return [Activity.model_validate(item) for item in load_dataset("activities", factory=list)]


@router.post("/generate", response_model=List[Activity])
def regenerate(payload: Dict[str, int] | None = None) -> List[Activity]:
    seed = (payload or {}).get("seed")
    return generate_activities(seed=seed)

