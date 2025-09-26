from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import Quest, StoryPrompt
from ..services import add_quest, craft_quest, delete_quest, get_world

router = APIRouter(prefix="/quests", tags=["quests"])


@router.get("", response_model=list[Quest])
def list_quests() -> list[Quest]:
    return list(get_world().quests)


@router.post("", response_model=Quest)
def create_quest(quest: Quest) -> Quest:
    return add_quest(quest)


@router.post("/craft", response_model=Quest)
def craft_from_prompt(prompt: StoryPrompt) -> Quest:
    quest = craft_quest(prompt)
    return add_quest(quest)


@router.put("/{quest_id}", response_model=Quest)
def update_quest(quest_id: str, payload: Quest) -> Quest:
    return add_quest(payload.model_copy(update={"id": quest_id}))


@router.delete("/{quest_id}", status_code=204)
def remove_quest(quest_id: str) -> None:
    if not get_world().find_quest(quest_id):
        raise HTTPException(status_code=404, detail="Quest not found")
    delete_quest(quest_id)
