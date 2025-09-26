from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class Tuning(BaseModel):
    food_per_capita: float
    import_factor: Dict[str, float] = Field(default_factory=dict)
    crime_coeffs: Dict[str, float] = Field(default_factory=dict)
    stability_thresholds: Dict[str, float] = Field(default_factory=dict)
    influence_drift: Dict[str, float] = Field(default_factory=dict)
    gold_per_min: float
    price_index_clamp: Dict[str, float] = Field(default_factory=dict)
