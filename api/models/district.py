from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class District(BaseModel):
    district_id: str
    city_id: str
    type: str
    footprint_area_km2: float
    density_target: float
    population: int
    crime_base: float
    guard_coverage_base: float
    landmark_tags: List[str] = Field(default_factory=list)

    @property
    def population_cap(self) -> float:
        return self.footprint_area_km2 * self.density_target

    def coverage_ratio(self) -> float:
        cap = self.population_cap
        if cap <= 0:
            return 0.0
        return min(1.0, self.population / cap)
