from __future__ import annotations

from typing import List, Optional

from nicegui import ui

from api.models import Quest, QuestStep, StoryPrompt
from api.services import add_quest, craft_quest, delete_quest, get_world


def quests_view() -> None:
    table = ui.table(
        title="Questline",
        columns=[
            {"name": "title", "label": "Tiêu đề", "field": "title"},
            {"name": "arc", "label": "Arc", "field": "arc"},
            {"name": "steps", "label": "Số bước", "field": "steps"},
        ],
        rows=[],
        row_key="id",
    ).classes("w-full")

    def open_editor(quest: Optional[Quest] = None) -> None:
        dialog = ui.dialog()
        steps: List[QuestStep] = list(quest.steps) if quest else []

        def close_and_refresh() -> None:
            dialog.close()
            refresh()

        with dialog, ui.card().classes("w-[520px]"):
            ui.label("Chỉnh sửa Quest" if quest else "Thêm Quest").classes("font-semibold text-lg")
            title_input = ui.input("Tiêu đề", value=quest.title if quest else "")
            arc_input = ui.input("Arc", value=quest.arc if quest else "Main")
            synopsis_input = ui.textarea("Tóm tắt", value=quest.synopsis if quest else "")
            level_input = ui.number("Level khuyến nghị", value=quest.recommended_level if quest else 20, format="%.0f")

            steps_column = ui.column().classes("w-full gap-2 mt-3")

            def render_steps() -> None:
                steps_column.clear()
                if not steps:
                    with steps_column:
                        ui.label("Chưa có bước").classes("text-sm text-slate-500")
                    return
                for idx, step in enumerate(steps):
                    with steps_column:
                        with ui.card().classes("w-full bg-slate-50"):
                            ui.label(f"Bước {idx + 1}").classes("text-sm text-slate-500")
                            title = ui.input("Tiêu đề", value=step.title)
                            description = ui.textarea("Mô tả", value=step.description)
                            encounter = ui.input("Kiểu encounter", value=step.encounter_type)
                            poi = ui.input("POI", value=step.poi_id or "")
                            npc = ui.input("NPC", value=step.npc_id or "")

                            def save_step(target: QuestStep = step, title_input=title, desc_input=description, encounter_input=encounter, poi_input=poi, npc_input=npc) -> None:
                                target.title = title_input.value or target.title
                                target.description = desc_input.value or target.description
                                target.encounter_type = encounter_input.value or target.encounter_type
                                target.poi_id = poi_input.value or None
                                target.npc_id = npc_input.value or None

                            ui.button("Lưu", on_click=save_step)
                            ui.button("Xóa", on_click=lambda s=step: (steps.remove(s), render_steps()), color="negative")

            def add_step() -> None:
                steps.append(QuestStep(title="Bước mới", description=""))
                render_steps()

            ui.button("Thêm bước", on_click=add_step).classes("mt-2")
            render_steps()

            def save_quest() -> None:
                payload = Quest(
                    id=quest.id if quest else None,  # type: ignore[arg-type]
                    title=title_input.value or "Quest mới",
                    synopsis=synopsis_input.value or "",
                    arc=arc_input.value or "Main",
                    recommended_level=int(level_input.value or 1),
                    steps=steps,
                )
                add_quest(payload)
                ui.notify("Đã lưu quest", color="positive")
                close_and_refresh()

            with ui.row().classes("gap-2 mt-3"):
                ui.button("Lưu", on_click=save_quest, color="primary")
                if quest:
                    ui.button(
                        "Xóa", on_click=lambda: (delete_quest(quest.id), close_and_refresh(), ui.notify("Đã xóa", color="warning")),
                        color="negative",
                    )
                ui.button("Đóng", on_click=close_and_refresh)

        dialog.open()

    def refresh() -> None:
        world = get_world(refresh=True)
        table.rows = [
            {
                "id": quest.id,
                "title": quest.title,
                "arc": quest.arc,
                "steps": len(quest.steps),
            }
            for quest in world.quests
        ]

    def handle_row(e) -> None:
        row = e.args.get("row", {}) if isinstance(e.args, dict) else {}
        quest_id = row.get("id") if isinstance(row, dict) else None
        if quest_id:
            quest = get_world().find_quest(quest_id)
            if quest:
                open_editor(quest)

    with ui.card().classes("w-full mt-4"):
        ui.label("Tạo quest từ prompt").classes("font-semibold text-lg")
        prompt_input = ui.textarea("Đề bài", placeholder="Ví dụ: Giải cứu đoàn thương nhân khỏi bọn cướp trên sông.")
        steps_input = ui.number("Số bước", value=4, min=1, max=8, format="%.0f")
        seed_input = ui.number("Seed", value=0, min=0, format="%.0f")

        def craft_from_prompt() -> None:
            prompt = prompt_input.value or "Quest vô danh"
            quest = craft_quest(StoryPrompt(prompt=prompt, steps=int(steps_input.value or 4), seed=int(seed_input.value or 0)))
            add_quest(quest)
            ui.notify("Đã tạo quest", color="positive")
            refresh()

        ui.button("Generate", on_click=craft_from_prompt, color="primary")

    table.on("row-click", handle_row)
    ui.button("Thêm quest", on_click=lambda: open_editor(None)).classes("mt-2")
    refresh()
