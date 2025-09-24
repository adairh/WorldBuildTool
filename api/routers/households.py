from typing import List

from fastapi import APIRouter, Query

from ..schemas import Household
from ..services import generate_households

router = APIRouter(prefix="/households", tags=["households"])


@router.get("/preview", response_model=List[Household])
def preview_households(
    count: int = Query(6, ge=1, le=48, description="Number of households to synthesize"),
    seed: int = Query(42, description="Seed for deterministic generation"),
) -> List[Household]:
    """Generate sample households with relationships, ledger info, and traits."""

    return generate_households(count=count, seed=seed)


@router.get("/archetypes", response_model=List[str])
def household_archetypes() -> List[str]:
    """Expose narrative archetypes for design reference."""

    return [
        "Royal courier families balancing loyalty and intrigue",
        "River wardens policing illicit qi trafficking",
        "Martial academies shielding prodigies from rival sects",
        "Merchant guild clans financing rebellion and court life simultaneously",
    ]
