from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class FestivalEffects(BaseModel):
    vendor_boost_pct: float = 0.0
    crime_shift: float = 0.0
    guard_shift: float = 0.0
    price_delta_pct: float = 0.0
    spawn_overrides: List[str] = Field(default_factory=list)
    quest_unlock_tags: List[str] = Field(default_factory=list)


class Festival(BaseModel):
    festival_id: str
    name: str
    month: int
    day: int
    duration_days: int
    primary_zone: str
    secondary_zones: List[str] = Field(default_factory=list)
    theme: str
    effects: FestivalEffects = Field(default_factory=FestivalEffects)
