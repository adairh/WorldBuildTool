from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .person import Person


class HouseholdLocation(BaseModel):
    poi_id: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None


class HouseholdLedger(BaseModel):
    silver: int = 0
    rice: int = 0
    influence: int = 0
    artisans: int = 0


class Household(BaseModel):
    household_id: str
    house_type: str = "nhà 3 gian"
    status: str = "occupied"
    district: Optional[str] = None
    allegiance: Optional[str] = None
    specialty: Optional[str] = None
    location: HouseholdLocation = Field(default_factory=HouseholdLocation)
    members: List[Person] = Field(default_factory=list)
    notes: Optional[str] = None
    ledger: HouseholdLedger = Field(default_factory=HouseholdLedger)

    def member_names(self) -> List[str]:
        return [member.name for member in self.members]
