from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ReputationGate(BaseModel):
    faction_id: str
    min: int


class AccessRequirements(BaseModel):
    story_flags: List[str] = Field(default_factory=list)
    reputation: List[ReputationGate] = Field(default_factory=list)
    attire_tags: List[str] = Field(default_factory=list)
    bribe_allowed: bool = False


class AccessRule(BaseModel):
    access_rule_id: str
    requires: AccessRequirements
