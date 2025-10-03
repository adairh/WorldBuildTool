from fastapi import APIRouter

from . import areas, export, professions, state

router = APIRouter()
router.include_router(professions.router, prefix="/professions", tags=["professions"])
router.include_router(areas.router, prefix="/areas", tags=["areas"])
router.include_router(state.router, prefix="/state", tags=["state"])
router.include_router(export.router, prefix="/export", tags=["export"])
