from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class Event(BaseModel):
    event_id: str
    date: date
    title: str
    description: str = ""
    linked_poi_ids: List[str] = Field(default_factory=list)
    linked_person_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    def occurs_in_decade(self, decade_start: int) -> bool:
        return decade_start <= self.date.year < decade_start + 10

    def involves(self, poi_id: Optional[str] = None, person_id: Optional[str] = None) -> bool:
        if poi_id and poi_id in self.linked_poi_ids:
            return True
        if person_id and person_id in self.linked_person_ids:
            return True
        return False
