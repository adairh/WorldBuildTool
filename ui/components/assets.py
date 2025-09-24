from nicegui import ui

from api.schemas import WorldRequest
from api.services import generate_world


def asset_view() -> None:
    """Preview generated asset prompts for art and audio teams."""

    bundle = generate_world(WorldRequest(seed=112, household_count=5, quest_count=3, event_count=7))
    with ui.column().classes("gap-2"):
        ui.label("Asset Studio").classes("text-2xl font-semibold")
        for asset in bundle.assets[:10]:
            with ui.card():
                ui.label(f"{asset.name} [{asset.category}]")
                ui.label(asset.prompt)
                ui.label(f"Storage Path: {asset.storagePath}")
