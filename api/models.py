from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


class Profession(BaseModel):
    id: str = Field(default_factory=lambda: _generate_id("prof"))
    name: str
    description: str = ""


class Area(BaseModel):
    id: str = Field(default_factory=lambda: _generate_id("area"))
    name: str
    description: str = ""
    notes: str = ""
    planned_households: int = Field(default=0, ge=0)


class HouseholdMember(BaseModel):
    id: str = Field(default_factory=lambda: _generate_id("mem"))
    name: str
    age: int = Field(ge=0)
    gender: str
    relation: str


class Household(BaseModel):
    id: str = Field(default_factory=lambda: _generate_id("hh"))
    area_id: str
    profession_id: str
    people_count: int = Field(ge=1)
    traits: List[str] = Field(default_factory=list)
    notes: str = ""
    members: List[HouseholdMember] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    evaluation_feedback: Optional[str] = None

    @validator("traits", pre=True, always=True)
    def ensure_unique_traits(cls, value: List[str]):  # type: ignore[override]
        unique = []
        for item in value or []:
            if item and item not in unique:
                unique.append(item)
        return unique


class WorldState(BaseModel):
    professions: List[Profession] = Field(default_factory=list)
    areas: List[Area] = Field(default_factory=list)
    households: List[Household] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()

    def find_area(self, area_id: str) -> Area:
        for area in self.areas:
            if area.id == area_id:
                return area
        raise KeyError(f"Area {area_id} not found")

    def find_profession(self, profession_id: str) -> Profession:
        for prof in self.professions:
            if prof.id == profession_id:
                return prof
        raise KeyError(f"Profession {profession_id} not found")

    def households_by_area(self, area_id: str) -> List[Household]:
        return [h for h in self.households if h.area_id == area_id]


def empty_world() -> WorldState:
    return WorldState()
