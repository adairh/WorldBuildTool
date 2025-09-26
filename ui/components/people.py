from __future__ import annotations

from typing import Dict, List

from nicegui import ui

from api.models import Household, Person
from api.services import generate_households, validation_summary
from api.storage import load_dataset


def _load_households() -> List[Household]:
    return [Household.model_validate(item) for item in load_dataset("households", factory=list)]


def _load_people() -> List[Person]:
    return [Person.model_validate(item) for item in load_dataset("persons", factory=list)]


def people_view() -> None:
    """People & Lore pillar."""

    with ui.row().classes("gap-4 items-end"):
        count_input = ui.number("Số hộ cần sinh", value=5, min=1, max=200).classes("w-40")
        seed_input = ui.number("Seed", value=42, min=0).classes("w-40")

        def trigger_generation() -> None:
            try:
                generate_households(int(count_input.value or 1), seed=int(seed_input.value or 0))
            except ValueError as exc:
                ui.notify(str(exc), color="negative")
                return
            refresh_tables()
            ui.notify("Đã sinh hộ dân mới")

        ui.button("Generate", on_click=trigger_generation)

    household_table = ui.table(
        columns=[
            {"name": "household_id", "label": "Hộ", "field": "household_id"},
            {"name": "house_type", "label": "Loại nhà", "field": "house_type"},
            {"name": "district", "label": "Quận", "field": "district"},
            {"name": "ledger", "label": "Tài sản", "field": "ledger"},
            {"name": "members", "label": "Thành viên", "field": "members"},
        ],
        rows=[],
        row_key="household_id",
    ).classes("w-full")

    person_table = ui.table(
        columns=[
            {"name": "person_id", "label": "ID", "field": "person_id"},
            {"name": "name", "label": "Tên", "field": "name"},
            {"name": "profession", "label": "Nghề", "field": "profession"},
            {"name": "household_id", "label": "Hộ", "field": "household_id"},
        ],
        rows=[],
        row_key="person_id",
    ).classes("w-full")

    mix_table = ui.table(
        columns=[
            {"name": "district", "label": "Quận", "field": "district"},
            {"name": "archetype", "label": "Kiểu NPC", "field": "archetype"},
            {"name": "ratio", "label": "Tỷ lệ", "field": "ratio"},
        ],
        rows=[],
        row_key="row_id",
    ).classes("w-full mt-6")

    coverage_card = ui.card().classes("w-full bg-slate-900 text-slate-100 mt-4")

    def refresh_tables() -> None:
        summary = validation_summary()
        households = _load_households()
        people = _load_people()
        household_table.rows = [
            {
                "household_id": household.household_id,
                "house_type": household.house_type,
                "district": household.district or "-",
                "ledger": f"Agri:{household.ledger.rice} / Silver:{household.ledger.silver}",
                "members": ", ".join(member.name for member in household.members),
            }
            for household in households
        ]
        person_table.rows = [
            {
                "person_id": person.person_id,
                "name": person.name,
                "profession": person.profession or "",
                "household_id": person.household_id or "",
            }
            for person in people
        ]
        npc_mix: List[Dict[str, object]] = [
            {"row_id": f"{item['district_id']}::{item['archetype']}", "district": item["district_id"], "archetype": item["archetype"], "ratio": item["ratio"]}
            for item in load_dataset("npc_mix", factory=list)
        ]
        mix_table.rows = npc_mix

        coverage = summary.get("coverage_matrix", {})
        district_stats = summary.get("districts", {})
        coverage_card.clear()
        with coverage_card:
            ui.label("District Coverage & Guard Readiness").classes("text-lg font-semibold")
            ui.table(
                columns=[
                    {"name": "district", "label": "Quận", "field": "district"},
                    {"name": "quests", "label": "Quest", "field": "quests"},
                    {"name": "vendors", "label": "Vendor", "field": "vendors"},
                    {"name": "guard", "label": "Guard", "field": "guard"},
                    {"name": "crime", "label": "Tội phạm", "field": "crime"},
                ],
                rows=[
                    {
                        "district": district,
                        "quests": data.get("quests"),
                        "vendors": data.get("vendors"),
                        "guard": "✅" if data.get("guard_ready") else "⚠️",
                        "crime": district_stats.get(district, {}).get("crime_expected"),
                    }
                    for district, data in coverage.items()
                ],
            ).classes("w-full")

    refresh_tables()
