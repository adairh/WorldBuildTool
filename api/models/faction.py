from __future__ import annotations

from pydantic import BaseModel


class FactionPresence(BaseModel):
    faction_id: str
    district_id: str
    influence: int


class Hostility(BaseModel):
    faction_a: str
    faction_b: str
    value: int
