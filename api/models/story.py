from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class StoryBeat(BaseModel):
    """Describe a major beat inside a narrative arc."""

    beat_id: str
    quest_id: str
    stage: str
    description: str
    poi_id: str
    timeline_ref: str
    tone: str = ""
    requires_cinematic: bool = False


class StoryArc(BaseModel):
    """High level story arc grouping questlines and beats."""

    arc_id: str
    name: str
    arc_type: str
    focus: str
    coverage_hubs: List[str] = Field(default_factory=list)
    questline_ids: List[str] = Field(default_factory=list)
    beats: List[StoryBeat] = Field(default_factory=list)
    cinematic_hooks: List[str] = Field(default_factory=list)
    approvals: List[str] = Field(default_factory=list)


class QuestMetric(BaseModel):
    """Aggregated quest analytics for dashboards."""

    quest_id: str
    length: int
    has_combat: bool
    has_social: bool
    has_traversal: bool
    fetch_chain: int


class NarrativeCoverage(BaseModel):
    """Coverage indicator for hubs across arcs and questlines."""

    hub_id: str
    story_percentage: float = 0.0
    active_arcs: List[str] = Field(default_factory=list)
    missing_elements: List[str] = Field(default_factory=list)

