from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..models import Household
from ..services import generate_households
from ..storage import load_dataset

router = APIRouter(prefix="/households", tags=["households"])


class HouseholdGenerateRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=200)
    seed: Optional[int] = None
    poi_pool: Optional[List[str]] = None


def _load_households() -> List[Household]:
    return [Household.model_validate(item) for item in load_dataset("households", factory=list)]


@router.get("", response_model=List[Household])
async def list_households() -> List[Household]:
    return _load_households()


@router.get("/{household_id}", response_model=Household)
async def get_household(household_id: str) -> Household:
    for household in _load_households():
        if household.household_id == household_id:
            return household
    raise HTTPException(status_code=404, detail="Household not found")


@router.post("/generate", response_model=List[Household])
async def generate(request: HouseholdGenerateRequest) -> List[Household]:
    households = generate_households(request.count, seed=request.seed, poi_pool=request.poi_pool)
    return households
