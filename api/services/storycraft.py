from __future__ import annotations

import random
from typing import List

from ..models import Quest, QuestStep, StoryPrompt

try:  # pragma: no cover - optional dependency
    import openai  # type: ignore
except Exception:  # pragma: no cover
    openai = None


def _fallback_steps(prompt: StoryPrompt) -> List[str]:
    seed = prompt.seed if prompt.seed is not None else sum(map(ord, prompt.prompt))
    random.seed(seed)
    verbs = ["Điều tra", "Đàm phán", "Bảo vệ", "Khám phá", "Trấn áp", "Đàm luận"]
    nouns = ["bí ẩn", "liên minh", "buổi lễ", "hành trình", "âm mưu", "di tích"]
    return [
        f"{random.choice(verbs)} {random.choice(nouns)} ở {prompt.prompt.split()[0]}"
        for _ in range(prompt.steps)
    ]


def _openai_steps(prompt: StoryPrompt) -> List[str]:  # pragma: no cover - network
    if not openai:
        return _fallback_steps(prompt)
    api_key = getattr(openai, "api_key", None)
    if not api_key:
        return _fallback_steps(prompt)
    completion = openai.ChatCompletion.create(  # type: ignore[attr-defined]
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert MMORPG quest designer."},
            {
                "role": "user",
                "content": f"Draft {prompt.steps} quest beats for Thang Long Wuxia based on: {prompt.prompt}",
            },
        ],
    )
    message = completion.choices[0].message["content"]  # type: ignore[index]
    lines = [line.strip("-• ") for line in message.splitlines() if line.strip()]
    if len(lines) >= prompt.steps:
        return lines[: prompt.steps]
    lines.extend(_fallback_steps(prompt)[len(lines) : prompt.steps])
    return lines


def craft_quest(prompt: StoryPrompt) -> Quest:
    beats = _openai_steps(prompt)
    steps = [
        QuestStep(title=beat, description=f"{prompt.prompt}\n\n{beat}", encounter_type="story")
        for beat in beats
    ]
    return Quest(title=prompt.prompt.strip().capitalize(), synopsis=prompt.prompt, steps=steps)
