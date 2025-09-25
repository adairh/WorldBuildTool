from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    person_id: str
    name: str
    birth_year: int
    sex: str
    profession: Optional[str] = None
    household_id: Optional[str] = None
    home_poi_id: Optional[str] = None
    relation: Optional[str] = None
    notes: Optional[str] = None

    def age_in_year(self, year: int) -> Optional[int]:
        return year - self.birth_year if year >= self.birth_year else None
