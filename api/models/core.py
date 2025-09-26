from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class MapLayer(BaseModel):
    name: str
    description: str = ""
    color: str = "#f97316"
    visible: bool = True


class MapSettings(BaseModel):
    base_image: Optional[str] = None
    width: int = 2048
    height: int = 2048
    layers: List[MapLayer] = Field(default_factory=lambda: [MapLayer(name="general", description="Lớp tổng quan")])

    def ensure_layer(self, name: str) -> None:
        if name and name not in {layer.name for layer in self.layers}:
            self.layers.append(MapLayer(name=name))


class POI(BaseModel):
    id: str = Field(default_factory=lambda: f"POI-{uuid4().hex[:8]}")
    name: str
    description: str = ""
    layer: str = "general"
    x: float = 0.0
    y: float = 0.0
    tags: List[str] = Field(default_factory=list)
    media: List[str] = Field(default_factory=list)


class Person(BaseModel):
    id: str = Field(default_factory=lambda: f"P-{uuid4().hex[:8]}")
    name: str
    birth_year: int
    sex: str = "U"
    profession: Optional[str] = None

    @property
    def age(self) -> int:
        return date.today().year - self.birth_year


class Household(BaseModel):
    id: str = Field(default_factory=lambda: f"HH-{uuid4().hex[:6]}")
    name: str
    home_poi_id: Optional[str] = None
    notes: str = ""
    members: List[Person] = Field(default_factory=list)


class QuestStep(BaseModel):
    id: str = Field(default_factory=lambda: f"QS-{uuid4().hex[:8]}")
    title: str
    description: str = ""
    poi_id: Optional[str] = None
    npc_id: Optional[str] = None
    encounter_type: str = "story"


class Quest(BaseModel):
    id: str = Field(default_factory=lambda: f"Q-{uuid4().hex[:8]}")
    title: str
    synopsis: str = ""
    arc: str = "Main"
    recommended_level: int = 20
    steps: List[QuestStep] = Field(default_factory=list)


class Event(BaseModel):
    id: str = Field(default_factory=lambda: f"EV-{uuid4().hex[:8]}")
    title: str
    date: str
    description: str = ""
    poi_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        date.fromisoformat(value)  # raises if invalid
        return value


class Asset(BaseModel):
    id: str = Field(default_factory=lambda: f"A-{uuid4().hex[:8]}")
    name: str
    kind: str = "concept"
    status: str = "draft"
    owner: str = "designer"
    tags: List[str] = Field(default_factory=list)
    notes: str = ""
    reference: Optional[str] = None


class WorldNote(BaseModel):
    id: str = Field(default_factory=lambda: f"N-{uuid4().hex[:8]}")
    title: str
    body: str


class WorldState(BaseModel):
    map: MapSettings = Field(default_factory=MapSettings)
    pois: List[POI] = Field(default_factory=list)
    households: List[Household] = Field(default_factory=list)
    quests: List[Quest] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)
    assets: List[Asset] = Field(default_factory=list)
    notes: List[WorldNote] = Field(default_factory=list)

    def ensure_layer(self, layer: str) -> None:
        self.map.ensure_layer(layer)

    def find_poi(self, poi_id: str) -> Optional[POI]:
        return next((poi for poi in self.pois if poi.id == poi_id), None)

    def find_household(self, household_id: str) -> Optional[Household]:
        return next((hh for hh in self.households if hh.id == household_id), None)

    def find_quest(self, quest_id: str) -> Optional[Quest]:
        return next((quest for quest in self.quests if quest.id == quest_id), None)


class ExportBundle(BaseModel):
    filename: str
    path: str


class DashboardSnapshot(BaseModel):
    total_pois: int
    total_households: int
    total_npcs: int
    total_quests: int
    total_events: int
    map_layers: int
    coverage: dict


class StoryPrompt(BaseModel):
    prompt: str
    steps: int = 4
    seed: Optional[int] = None

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Steps must be >= 1")
        return value


def data_path_relative(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    return str(Path(path))
