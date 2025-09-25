from __future__ import annotations

from typing import List

from nicegui import ui

from api.models import Household, Person
from api.services import generate_households
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
            generate_households(int(count_input.value or 1), seed=int(seed_input.value or 0))
            refresh_tables()
            ui.notify("Đã sinh hộ dân mới")

        ui.button("Generate", on_click=trigger_generation)

    household_table = ui.table(
        columns=[
            {"name": "household_id", "label": "Hộ", "field": "household_id"},
            {"name": "house_type", "label": "Loại nhà", "field": "house_type"},
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

    def refresh_tables() -> None:
        households = _load_households()
        people = _load_people()
        household_table.rows = [
            {
                "household_id": household.household_id,
                "house_type": household.house_type,
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

    refresh_tables()
