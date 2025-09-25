from __future__ import annotations

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services import export_bundle, list_available_exports

router = APIRouter(prefix="/export", tags=["export"])


class ExportRequest(BaseModel):
    types: List[str] = Field(default_factory=lambda: ["pois", "households", "persons", "events"])
    format: str = Field(default="json", pattern="^(json|csv|unity)$")


@router.post("")
def create_export(request: ExportRequest) -> dict:
    path = export_bundle(request.types, fmt=request.format)
    return {"path": str(path)}


@router.get("", response_model=List[str])
def list_exports() -> List[str]:
    return [str(path) for path in list_available_exports()]
