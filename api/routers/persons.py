from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models.person import Person
from ..schemas import Person as PersonSchema
from ..services import generate_households

router = APIRouter(prefix="/persons", tags=["persons"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/preview", response_model=List[PersonSchema])
def preview_persons(
    households: int = Query(3, ge=1, le=24, description="How many households to sample"),
    seed: int = Query(42, description="Seed used for deterministic preview"),
) -> List[PersonSchema]:
    generated = generate_households(count=households, seed=seed)
    return [member for household in generated for member in household.members]


@router.get("/{person_id}", response_model=dict)
def get_person(person_id: str, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return {
        "id": person.id,
        "name": person.name,
        "birthYear": person.birthYear,
        "deathYear": person.deathYear,
        "sex": person.sex,
        "profession": person.profession,
        "householdId": person.householdId,
        "homePoiId": person.homePoiId,
    }


@router.get("/", response_model=List[dict])
def list_persons(db: Session = Depends(get_db)):
    persons = db.query(Person).all()
    return [
        {
            "id": person.id,
            "name": person.name,
            "birthYear": person.birthYear,
            "deathYear": person.deathYear,
            "sex": person.sex,
            "profession": person.profession,
            "householdId": person.householdId,
            "homePoiId": person.homePoiId,
        }
        for person in persons
    ]
