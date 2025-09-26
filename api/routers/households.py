from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import Household
from ..services import add_household, delete_household, get_world

router = APIRouter(prefix="/households", tags=["households"])


@router.get("", response_model=list[Household])
def list_households() -> list[Household]:
    return list(get_world().households)


@router.post("", response_model=Household)
def create_household(household: Household) -> Household:
    return add_household(household)


@router.put("/{household_id}", response_model=Household)
def update_household(household_id: str, payload: Household) -> Household:
    return add_household(payload.model_copy(update={"id": household_id}))


@router.delete("/{household_id}", status_code=204)
def remove_household(household_id: str) -> None:
    if not get_world().find_household(household_id):
        raise HTTPException(status_code=404, detail="Household not found")
    delete_household(household_id)
