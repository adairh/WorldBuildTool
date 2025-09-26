from __future__ import annotations

from ..models import Quest, QuestStep, StoryPrompt
from .chatgpt import get_chatgpt


def craft_quest(prompt: StoryPrompt) -> Quest:
    beats = get_chatgpt().quest_beats(prompt)
    steps = [
        QuestStep(title=beat, description=f"{prompt.prompt}\n\n{beat}", encounter_type="story")
        for beat in beats
    ]
    return Quest(title=prompt.prompt.strip().capitalize(), synopsis=prompt.prompt, steps=steps)
