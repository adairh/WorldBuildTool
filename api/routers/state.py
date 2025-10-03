from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import Household, HouseholdMember
from ..storage import load_memory, load_world, save_world

router = APIRouter()


@router.get("/")
def get_state() -> dict:
    state = load_world()
    return state.dict()


@router.get("/households")
def list_households() -> list[Household]:
    state = load_world()
    return state.households


@router.put("/households/{household_id}")
def update_household(household_id: str, payload: Household) -> Household:
    state = load_world()
    for idx, household in enumerate(state.households):
        if household.id == household_id:
            state.households[idx] = payload.copy(update={"id": household_id})
            save_world(state)
            return state.households[idx]
    raise HTTPException(status_code=404, detail="Household not found")


@router.delete("/households/{household_id}", status_code=204)
def delete_household(household_id: str) -> None:
    state = load_world()
    for idx, household in enumerate(state.households):
        if household.id == household_id:
            state.households.pop(idx)
            save_world(state)
            return
    raise HTTPException(status_code=404, detail="Household not found")


@router.put("/households/{household_id}/members/{member_id}")
def update_member(household_id: str, member_id: str, payload: HouseholdMember) -> Household:
    state = load_world()
    for household in state.households:
        if household.id == household_id:
            for idx, member in enumerate(household.members):
                if member.id == member_id:
                    household.members[idx] = payload.copy(update={"id": member_id})
                    household.people_count = max(household.people_count, len(household.members))
                    save_world(state)
                    return household
            raise HTTPException(status_code=404, detail="Member not found")
    raise HTTPException(status_code=404, detail="Household not found")


@router.post("/households/{household_id}/members", status_code=201)
def add_member(household_id: str, payload: HouseholdMember) -> Household:
    state = load_world()
    for household in state.households:
        if household.id == household_id:
            household.members.append(payload)
            household.people_count = max(household.people_count, len(household.members))
            save_world(state)
            return household
    raise HTTPException(status_code=404, detail="Household not found")


@router.delete("/households/{household_id}/members/{member_id}", status_code=204)
def delete_member(household_id: str, member_id: str) -> None:
    state = load_world()
    for household in state.households:
        if household.id == household_id:
            household.members = [m for m in household.members if m.id != member_id]
            household.people_count = max(household.people_count, len(household.members))
            save_world(state)
            return
    raise HTTPException(status_code=404, detail="Household not found")


@router.get("/memory")
def get_memory(limit: int = 50) -> list[dict]:
    return load_memory(limit)
