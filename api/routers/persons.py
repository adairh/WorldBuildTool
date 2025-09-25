from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, HTTPException

from ..models import Household, Person
from ..storage import load_dataset

router = APIRouter(prefix="/persons", tags=["persons"])


def _load_people() -> List[Person]:
    return [Person.model_validate(item) for item in load_dataset("persons", factory=list)]


def _load_households() -> List[Household]:
    return [Household.model_validate(item) for item in load_dataset("households", factory=list)]


@router.get("", response_model=List[Person])
async def list_people() -> List[Person]:
    return _load_people()


@router.get("/{person_id}", response_model=Person)
async def get_person(person_id: str) -> Person:
    for person in _load_people():
        if person.person_id == person_id:
            return person
    raise HTTPException(status_code=404, detail="Person not found")


@router.get("/{person_id}/relations")
async def get_relations(person_id: str) -> Dict[str, List[str]]:
    people = {person.person_id: person for person in _load_people()}
    person = people.get(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    relations: Dict[str, List[str]] = {"household": [], "same_profession": []}
    for household in _load_households():
        ids = [member.person_id for member in household.members]
        if person_id in ids:
            relations["household"] = [pid for pid in ids if pid != person_id]
            break

    for other in people.values():
        if other.person_id != person.person_id and other.profession == person.profession:
            relations["same_profession"].append(other.person_id)

    return relations
