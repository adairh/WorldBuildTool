from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class TradeNode(BaseModel):
    node_id: str
    district_id: str
    node_type: str


class TradeRoute(BaseModel):
    route_id: str
    from_node_id: str
    to_node_id: str
    distance_km: float
    terrain_share: Dict[str, float] = Field(default_factory=dict)

    def terrain_sum(self) -> float:
        return sum(self.terrain_share.values())
