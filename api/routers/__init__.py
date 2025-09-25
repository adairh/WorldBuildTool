from fastapi import APIRouter

from . import (
    activities,
    checker,
    events,
    export,
    features,
    households,
    items,
    monsters,
    persons,
    pois,
    quests,
    story,
    world,
)

api_router = APIRouter()
api_router.include_router(pois.router)
api_router.include_router(households.router)
api_router.include_router(persons.router)
api_router.include_router(events.router)
api_router.include_router(export.router)
api_router.include_router(checker.router)
api_router.include_router(world.router)
api_router.include_router(quests.router)
api_router.include_router(story.router)
api_router.include_router(monsters.router)
api_router.include_router(features.router)
api_router.include_router(items.router)
api_router.include_router(activities.router)

__all__ = ["api_router"]
