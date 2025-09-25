from __future__ import annotations

from typing import Dict, List

from nicegui import ui

from api.models import Quest, StoryArc
from api.services import generate_quests, generate_story_arcs
from api.storage import load_dataset


def _poi_name_map() -> Dict[str, str]:
    data = load_dataset("pois", factory=list)
    return {item.get("id"): item.get("properties", {}).get("name", item.get("id")) for item in data}


def _load_quests() -> List[Quest]:
    return [Quest.model_validate(item) for item in load_dataset("quests", factory=list)]


def _load_arcs() -> List[StoryArc]:
    return [StoryArc.model_validate(item) for item in load_dataset("story_arcs", factory=list)]


def story_view() -> None:
    """Narrative desk with quest graphs and story arcs."""

    ui.label("Story Arc Manager").classes("text-2xl font-semibold text-slate-100 mb-2")
    with ui.row().classes("gap-4 items-end"):
        quest_count = ui.number("Questline count", value=6, min=1, max=24).classes("w-40")
        seed = ui.number("Seed", value=42, min=0).classes("w-32")

        def regenerate_story() -> None:
            quests = generate_quests(int(quest_count.value or 6), seed=int(seed.value or 0))
            generate_story_arcs(quests, seed=int(seed.value or 0))
            refresh_tables()
            ui.notify("Đã tái tạo questline và story arc")

        ui.button("Regenerate arcs", on_click=regenerate_story).classes("bg-emerald-500 text-white")

    quest_table = ui.table(
        columns=[
            {"name": "quest_id", "label": "Quest", "field": "quest_id"},
            {"name": "title", "label": "Tiêu đề", "field": "title"},
            {"name": "length", "label": "Độ dài", "field": "length"},
            {"name": "tags", "label": "Variety", "field": "tags"},
        ],
        rows=[],
        row_key="quest_id",
    ).classes("w-full shadow-lg")

    arc_table = ui.table(
        columns=[
            {"name": "arc_id", "label": "Arc", "field": "arc_id"},
            {"name": "name", "label": "Tên", "field": "name"},
            {"name": "type", "label": "Loại", "field": "type"},
            {"name": "coverage", "label": "Coverage", "field": "coverage"},
            {"name": "cinematics", "label": "Cinematics", "field": "cinematics"},
        ],
        rows=[],
        row_key="arc_id",
    ).classes("w-full shadow-lg")

    def refresh_tables() -> None:
        quests = _load_quests()
        arcs = _load_arcs()
        poi_names = _poi_name_map()
        quest_table.rows = [
            {
                "quest_id": quest.quest_id,
                "title": quest.title,
                "length": len(quest.nodes),
                "tags": ", ".join(quest.tags) if hasattr(quest, "tags") else "",
            }
            for quest in quests
        ]
        arc_table.rows = [
            {
                "arc_id": arc.arc_id,
                "name": arc.name,
                "type": arc.arc_type,
                "coverage": ", ".join(poi_names.get(hub, hub) for hub in arc.coverage_hubs) or "(trống)",
                "cinematics": ", ".join(arc.cinematic_hooks) or "-",
            }
            for arc in arcs
        ]

    refresh_tables()

