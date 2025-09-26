from __future__ import annotations

from pydantic import BaseModel


class NPCMix(BaseModel):
    district_id: str
    archetype: str
    ratio: float

    def headcount(self, population: int) -> int:
        return round(self.ratio * population)
