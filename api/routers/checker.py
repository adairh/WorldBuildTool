from __future__ import annotations

from typing import List

from fastapi import APIRouter

from ..services import validate_world, validation_summary

router = APIRouter(prefix="/checker", tags=["checker"])


@router.get("/issues", response_model=List[str])
async def list_issues() -> List[str]:
    return validate_world()


@router.get("/summary")
async def get_summary() -> dict:
    return validation_summary()
