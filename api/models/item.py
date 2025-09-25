from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class LootSource(BaseModel):
    source_type: str  # monster, quest, feature, vendor, activity
    reference_id: str
    drop_rate: float
    notes: str = ""


class Item(BaseModel):
    item_id: str
    name: str
    slot: str
    rarity: str
    description: str
    progression_stage: str
    sources: List[LootSource] = Field(default_factory=list)


class LootHealth(BaseModel):
    item_id: str
    missing_sources: bool = False
    dominant_source: str = ""

