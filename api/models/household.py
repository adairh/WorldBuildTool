from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .person import Person


class HouseholdLocation(BaseModel):
    poi_id: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None


class Household(BaseModel):
    household_id: str
    house_type: str = "nhà 3 gian"
    status: str = "occupied"
    location: HouseholdLocation = Field(default_factory=HouseholdLocation)
    members: List[Person] = Field(default_factory=list)
    notes: Optional[str] = None

    def member_names(self) -> List[str]:
        return [member.name for member in self.members]
