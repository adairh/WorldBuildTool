from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class EncounterProfile(BaseModel):
    """A specific encounter template inside a monster zone."""

    encounter_id: str
    style: str  # combat, social, puzzle
    monster_types: List[str]
    spawn_weight: float
    recommended_power: str
    loot_table_ids: List[str] = Field(default_factory=list)
    notes: str = ""


class MonsterZone(BaseModel):
    """Polygonal spawn zone for creatures and encounters."""

    zone_id: str
    name: str
    faction: str
    anchor_poi_id: str
    level_range: List[int]
    polygon: List[List[float]]
    spawn_windows: List[str] = Field(default_factory=list)
    encounters: List[EncounterProfile] = Field(default_factory=list)


class EncounterVarietyMetric(BaseModel):
    """High level stats used in dashboards."""

    combat_ratio: float
    social_ratio: float
    puzzle_ratio: float

