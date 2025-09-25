from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DialogueNode(BaseModel):
    node_id: str
    speaker: str
    text: str
    choices: List[str] = Field(default_factory=list)


class Quest(BaseModel):
    quest_id: str
    title: str
    description: str = ""
    nodes: Dict[str, DialogueNode] = Field(default_factory=dict)
    start_node: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
