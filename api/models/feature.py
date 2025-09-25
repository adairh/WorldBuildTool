from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class FeatureSchedule(BaseModel):
    cadence: str
    seasons: List[str] = Field(default_factory=list)
    active_days: List[str] = Field(default_factory=list)


class GameplayFeature(BaseModel):
    feature_id: str
    feature_type: str
    poi_id: str
    unlock_condition: str
    required_level: str
    supports_groups: bool = True
    schedule: FeatureSchedule = Field(default_factory=lambda: FeatureSchedule(cadence="always"))
    notes: str = ""


class FeatureCoverage(BaseModel):
    hub_id: str
    essentials: List[str] = Field(default_factory=list)
    missing: List[str] = Field(default_factory=list)

