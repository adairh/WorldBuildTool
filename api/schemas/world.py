"""Pydantic models describing TL-Forge worldbuilding payloads."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

try:  # Pydantic v2+ provides ConfigDict
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover - fallback for pydantic v1
    ConfigDict = None  # type: ignore[assignment]


class Trait(BaseModel):
    """Describe a unique trait or quirk for a person or household."""

    name: str
    description: str


class Relationship(BaseModel):
    """Directional relationship metadata between two characters."""

    targetId: str = Field(..., description="Identifier of the related person")
    relation: str = Field(..., description="Type of relation such as ally, rival, sibling")
    intensity: int = Field(
        0,
        ge=-5,
        le=5,
        description="Sentiment intensity from -5 (hatred) to +5 (devotion)",
    )


class MartialStyle(BaseModel):
    name: str
    element: str
    hallmarkMove: str


class Person(BaseModel):
    """A person living in the Thăng Long inspired setting."""

    id: str
    name: str
    courtesyName: Optional[str] = None
    birthYear: int
    sex: str
    profession: Optional[str] = None
    cultivationStage: str = Field(..., description="Internal cultivation rank")
    martialStyle: MartialStyle
    notableTraits: List[Trait] = Field(default_factory=list)
    householdId: Optional[str] = None
    homePoiId: Optional[str] = None
    relationships: List[Relationship] = Field(default_factory=list)

    if ConfigDict is not None:  # pragma: no branch - pydantic v2 path
        model_config = ConfigDict(from_attributes=True)
    else:  # pragma: no cover - pydantic v1 compatibility
        class Config:  # type: ignore[no-redef]
            orm_mode = True


class HouseholdLedger(BaseModel):
    """Economic slice of a household."""

    silver: int
    rice: int
    artisans: int
    renown: int


class Household(BaseModel):
    """Household container that binds a clan in the city."""

    id: str
    name: str
    clan: str
    district: str
    specialty: str
    allegiance: str
    reputation: str
    foundingLegend: str
    members: List[Person]
    alliances: List[str] = Field(default_factory=list)
    rivals: List[str] = Field(default_factory=list)
    assets: List[str] = Field(default_factory=list)
    ledger: HouseholdLedger


class POI(BaseModel):
    id: str
    name: str
    category: str
    district: str
    description: str
    layers: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class Event(BaseModel):
    id: str
    year: int
    season: str
    title: str
    description: str
    primaryPoiId: Optional[str]
    participantIds: List[str]
    type: str
    outcome: str
    repercussions: List[str] = Field(default_factory=list)


class QuestChoice(BaseModel):
    id: str
    text: str
    skillCheck: Optional[str] = None
    nextNodeId: Optional[str] = None
    reputationShift: Dict[str, int] = Field(default_factory=dict)
    rewards: List[str] = Field(default_factory=list)


class QuestNode(BaseModel):
    id: str
    speaker: Optional[str] = None
    dialogue: str
    cinematicCue: Optional[str] = None
    choices: List[QuestChoice] = Field(default_factory=list)


class Quest(BaseModel):
    id: str
    title: str
    synopsis: str
    startingNodeId: str
    requiredReputation: Dict[str, int] = Field(default_factory=dict)
    nodes: Dict[str, QuestNode]
    rewards: List[str] = Field(default_factory=list)
    factionsInvolved: List[str] = Field(default_factory=list)


class Asset(BaseModel):
    id: str
    name: str
    category: str
    prompt: str
    storagePath: str
    attribution: Optional[str] = None


class EconomySnapshot(BaseModel):
    year: int
    totalSilver: int
    totalRice: int
    artisanCount: int
    reputationAverages: Dict[str, float]
    guildReports: Dict[str, str]


class NarrativeHook(BaseModel):
    id: str
    title: str
    pitch: str
    suggestedQuestId: Optional[str] = None
    tone: str


class WorldBundle(BaseModel):
    seed: int
    households: List[Household]
    persons: List[Person]
    pois: List[POI]
    events: List[Event]
    quests: List[Quest]
    assets: List[Asset]
    economy: EconomySnapshot
    narrativeHooks: List[NarrativeHook]


class WorldRequest(BaseModel):
    """Parameters accepted by the generator endpoint."""

    seed: int = 42
    household_count: int = Field(8, ge=1, le=64)
    quest_count: int = Field(5, ge=1, le=32)
    event_count: int = Field(12, ge=1, le=64)
    include_assets: bool = True
