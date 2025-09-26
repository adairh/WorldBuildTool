from fastapi import APIRouter

from . import assets, events, households, pois, quests, world

api_router = APIRouter()
api_router.include_router(world.router)
api_router.include_router(pois.router)
api_router.include_router(households.router)
api_router.include_router(quests.router)
api_router.include_router(events.router)
api_router.include_router(assets.router)

__all__ = ["api_router"]
