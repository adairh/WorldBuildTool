from nicegui import ui

from api.schemas import WorldRequest
from api.services import generate_world, summarize_world, validate_world


def world_view() -> None:
    """Dashboard summarizing a generated bundle."""

    request = WorldRequest(seed=128, household_count=6, quest_count=4, event_count=10)
    bundle = generate_world(request)
    summary = summarize_world(bundle)
    errors = validate_world(bundle)

    with ui.column().classes("gap-2"):
        ui.label("World Overview").classes("text-2xl font-semibold")
        ui.label(f"Seed: {summary['seed']}")
        with ui.row().classes("gap-2 flex-wrap"):
            for key in ["households", "persons", "pois", "events", "quests", "assets"]:
                with ui.card().classes("p-3"):
                    ui.label(key.title())
                    ui.label(str(summary[key]))
        with ui.card():
            ui.label("Economy Snapshot").classes("font-semibold")
            econ = summary["economy"]
            ui.label(f"Silver: {econ['totalSilver']}")
            ui.label(f"Rice: {econ['totalRice']}")
            ui.label(f"Artisans: {econ['artisanCount']}")
        with ui.card():
            ui.label("Narrative Hooks").classes("font-semibold")
            for hook in bundle.narrativeHooks:
                ui.label(f"{hook.title} ({hook.tone})")
                ui.label(hook.pitch)
        if errors:
            with ui.card().classes("bg-red-100"):
                ui.label(f"Validation Issues ({len(errors)})")
                for err in errors:
                    ui.label(err)
        else:
            ui.label("Validation clean").classes("text-green-500")
