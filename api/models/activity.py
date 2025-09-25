from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ActivitySchedule(BaseModel):
    cadence: str
    days: List[str] = Field(default_factory=list)
    seasons: List[str] = Field(default_factory=list)


class Activity(BaseModel):
    activity_id: str
    name: str
    activity_type: str
    poi_id: str
    summary: str
    rewards: List[str] = Field(default_factory=list)
    schedule: ActivitySchedule = Field(default_factory=lambda: ActivitySchedule(cadence="daily"))
    approvals: List[str] = Field(default_factory=list)


class ActivityCoverage(BaseModel):
    hub_id: str
    activity_count: int
    categories: List[str] = Field(default_factory=list)

