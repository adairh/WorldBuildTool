from fastapi import APIRouter

from . import events, export, households, persons, pois, quests, world

api_router = APIRouter()
api_router.include_router(persons.router)
api_router.include_router(households.router)
api_router.include_router(pois.router)
api_router.include_router(events.router)
api_router.include_router(quests.router)
api_router.include_router(export.router)
api_router.include_router(world.router)

__all__ = ["api_router"]
