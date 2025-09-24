from nicegui import ui

from api.schemas import WorldRequest
from api.services import generate_world


def people_view() -> None:
    """Display synthesized households and members with martial metadata."""

    bundle = generate_world(WorldRequest(seed=64, household_count=4, quest_count=2, event_count=6))
    with ui.column().classes("w-full gap-3"):
        ui.label("Household Cohorts").classes("text-2xl font-semibold")
        for household in bundle.households:
            with ui.card().classes("w-full"):
                ui.label(f"{household.name} — {household.reputation} ({household.district})")
                ui.label(f"Allegiance: {household.allegiance} | Specialty: {household.specialty}")
                ui.label(f"Ledger → Silver: {household.ledger.silver} • Rice: {household.ledger.rice}")
                for member in household.members:
                    with ui.row().classes("w-full justify-between text-sm"):
                        ui.label(f"{member.name} [{member.cultivationStage}]")
                        ui.label(f"Style: {member.martialStyle.name}")
                        ui.label(f"Profession: {member.profession}")
