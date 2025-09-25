from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from ..models import GameplayFeature
from ..services import generate_gameplay_features
from ..storage import load_dataset

router = APIRouter(prefix="/features", tags=["features"])


@router.get("", response_model=List[GameplayFeature])
def list_features() -> List[GameplayFeature]:
    return [GameplayFeature.model_validate(item) for item in load_dataset("features", factory=list)]


@router.post("/generate", response_model=List[GameplayFeature])
def regenerate(payload: Dict[str, int] | None = None) -> List[GameplayFeature]:
    seed = (payload or {}).get("seed")
    return generate_gameplay_features(seed=seed)

