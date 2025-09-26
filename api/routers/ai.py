from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import PromptRequest
from ..services.chatgpt import ai_channel_history, ai_memory_summary, clear_ai_channel, prompt_ai

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/prompt")
def run_prompt(request: PromptRequest) -> dict:
    response = prompt_ai(request)
    return {"response": response}


@router.get("/memory")
def memory() -> dict:
    return {"channels": ai_memory_summary()}


@router.get("/memory/{channel}")
def memory_channel(channel: str) -> dict:
    history = ai_channel_history(channel)
    if not history:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"channel": channel, "history": history}


@router.delete("/memory/{channel}", status_code=204)
def memory_clear(channel: str) -> None:
    clear_ai_channel(channel)
