from __future__ import annotations

from pydantic import BaseModel


class LawCrimeParams(BaseModel):
    city_id: str
    lawfulness_base: float
    high_crime_threshold: float
    guard_effectiveness: float


class DistrictCrimeOverride(BaseModel):
    district_id: str
    hotspot: bool = False
    black_market_flag: bool = False
