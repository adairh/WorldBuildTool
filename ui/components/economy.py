from nicegui import ui

from api.schemas import WorldRequest
from api.services import generate_world


def economy_view() -> None:
    """Show derived economy analytics."""

    bundle = generate_world(WorldRequest(seed=140, household_count=6, quest_count=3, event_count=8))
    econ = bundle.economy

    with ui.column().classes("gap-2"):
        ui.label("Economy Lite").classes("text-2xl font-semibold")
        ui.label(f"Total Silver: {econ.totalSilver}")
        ui.label(f"Total Rice: {econ.totalRice}")
        ui.label(f"Artisans Mobilized: {econ.artisanCount}")
        with ui.card():
            ui.label("Reputation Averages").classes("font-semibold")
            for faction, value in econ.reputationAverages.items():
                ui.label(f"{faction}: {value}")
        with ui.card():
            ui.label("Guild Reports").classes("font-semibold")
            for guild, report in econ.guildReports.items():
                ui.label(f"{guild}: {report}")
