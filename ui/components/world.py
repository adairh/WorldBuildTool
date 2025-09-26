from __future__ import annotations

from nicegui import ui

from api.services import get_world, world_summary


def world_view() -> None:
    summary = world_summary()
    world = get_world()

    with ui.row().classes("w-full gap-4"):
        for label, value in [
            ("Điểm mốc", summary["total_pois"]),
            ("Hộ dân", summary["total_households"]),
            ("NPC", summary["total_npcs"]),
            ("Quest", summary["total_quests"]),
            ("Sự kiện", summary["total_events"]),
        ]:
            ui.card().classes("bg-slate-900 text-slate-100 p-4 w-48").with_slots(lambda l=label, v=value: (
                ui.label(l).classes("text-sm uppercase text-slate-400"),
                ui.label(str(v)).classes("text-2xl font-semibold mt-1"),
            ))

    with ui.row().classes("w-full mt-4"):
        coverage_card = ui.card().classes("w-full")
        with coverage_card:
            ui.label("Layer Coverage").classes("font-semibold text-lg")
            ui.table(
                columns=[
                    {"name": "layer", "label": "Layer", "field": "layer"},
                    {"name": "count", "label": "POI", "field": "count"},
                ],
                rows=[{"layer": layer, "count": count} for layer, count in summary["coverage"].items()],
            )

    with ui.row().classes("w-full mt-4"):
        note_card = ui.card().classes("w-full")
        note_card.classes("bg-white")
        with note_card:
            ui.label("Ghi chú thế giới").classes("font-semibold text-lg")
            if not world.notes:
                ui.label("Chưa có ghi chú.")
            for note in world.notes:
                with ui.expansion(note.title, value=False).classes("w-full"):
                    ui.markdown(note.body or "(Trống)")
