from __future__ import annotations

from typing import List

from pydantic import BaseModel


class LevelBand(BaseModel):
    min: int
    max: int


class City(BaseModel):
    city_id: str
    name: str
    role: str
    level_band: LevelBand
    population_target: int
    food_import_need: float
    stability_target: float
    entry_gates: List[str]
    wharves: List[str]
