from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class GaugeMetric(BaseModel):
    name: str
    value: float
    target: float
    description: str = ""


class FunnelMetric(BaseModel):
    stages: List[Dict[str, float]] = Field(default_factory=list)


class DashboardSnapshot(BaseModel):
    story_coverage: GaugeMetric
    monster_variety: GaugeMetric
    feature_coverage: GaugeMetric
    loot_health: GaugeMetric
    export_ready: GaugeMetric
    activity_coverage: GaugeMetric
    faction_matrix: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    encounter_variety: Dict[str, float] = Field(default_factory=dict)
    loot_sources: Dict[str, float] = Field(default_factory=dict)
    schedule_overview: Dict[str, List[str]] = Field(default_factory=dict)
    rule_violations: FunnelMetric = Field(default_factory=FunnelMetric)

