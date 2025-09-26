from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Geometry(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(default_factory=lambda: [0.0, 0.0])


class POIProperties(BaseModel):
    name: str
    kind: str = "generic"
    layers: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    description: str = ""
    media: List[str] = Field(default_factory=list)
    owner_faction_id: str | None = None
    open_hours: List[str] = Field(default_factory=list)
    capacity: int = 0
    services: List[str] = Field(default_factory=list)
    access_rule_id: str | None = None


class POI(BaseModel):
    id: str
    district_id: str
    geometry: Geometry
    properties: POIProperties

    def summary(self) -> str:
        return f"{self.properties.name} ({', '.join(self.properties.layers) or 'unlayered'})"
