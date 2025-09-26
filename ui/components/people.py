from __future__ import annotations

from typing import List, Optional

from nicegui import ui

from api.models import Household, Person
from api.services import add_household, delete_household, get_world


def people_view() -> None:
    table = ui.table(
        title="Hộ gia đình",
        columns=[
            {"name": "name", "label": "Tên hộ", "field": "name"},
            {"name": "members", "label": "Thành viên", "field": "members"},
            {"name": "home", "label": "POI", "field": "home"},
        ],
        rows=[],
        row_key="id",
    ).classes("w-full")

    def open_editor(household: Optional[Household] = None) -> None:
        dialog = ui.dialog()
        members: List[Person] = list(household.members) if household else []

        def close_and_refresh() -> None:
            dialog.close()
            refresh()

        with dialog, ui.card().classes("w-[480px]"):
            ui.label("Chỉnh sửa hộ" if household else "Thêm hộ").classes("font-semibold text-lg")
            name_input = ui.input("Tên hộ", value=household.name if household else "")
            poi_input = ui.input("POI ID", value=household.home_poi_id if household else "")
            note_input = ui.textarea("Ghi chú", value=household.notes if household else "")

            member_column = ui.column().classes("gap-2 w-full mt-3")

            def render_members() -> None:
                member_column.clear()
                if not members:
                    with member_column:
                        ui.label("Chưa có thành viên.").classes("text-sm text-slate-500")
                    return
                for idx, person in enumerate(members):
                    with member_column:
                        with ui.card().classes("w-full bg-slate-50"):
                            ui.label(f"Thành viên {idx + 1}").classes("text-sm text-slate-500")
                            name = ui.input("Tên", value=person.name)
                            birth = ui.number("Năm sinh", value=person.birth_year, format="%.0f")
                            sex = ui.input("Giới tính", value=person.sex)
                            profession = ui.input("Nghề", value=person.profession or "")

                            def save_member(target: Person = person, name_input=name, birth_input=birth, sex_input=sex, profession_input=profession) -> None:
                                target.name = name_input.value or target.name
                                target.birth_year = int(birth_input.value or target.birth_year)
                                target.sex = sex_input.value or target.sex
                                target.profession = profession_input.value or None

                            ui.button("Lưu", on_click=save_member)
                            ui.button("Xóa", on_click=lambda p=person: (members.remove(p), render_members()), color="negative")

            def add_member() -> None:
                members.append(Person(name="Tên mới", birth_year=1280, sex="M"))
                render_members()

            ui.button("Thêm thành viên", on_click=add_member).classes("mt-2")
            render_members()

            def save_household() -> None:
                payload = Household(
                    id=household.id if household else None,  # type: ignore[arg-type]
                    name=name_input.value or "Hộ mới",
                    home_poi_id=poi_input.value or None,
                    notes=note_input.value or "",
                    members=members,
                )
                add_household(payload)
                ui.notify("Đã lưu hộ", color="positive")
                close_and_refresh()

            with ui.row().classes("w-full gap-2 mt-3"):
                ui.button("Lưu", on_click=save_household, color="primary")
                if household:
                    ui.button(
                        "Xóa", on_click=lambda: (delete_household(household.id), close_and_refresh(), ui.notify("Đã xóa", color="warning")),
                        color="negative",
                    )
                ui.button("Đóng", on_click=close_and_refresh)

        dialog.open()

    def refresh() -> None:
        world = get_world(refresh=True)
        table.rows = [
            {
                "id": household.id,
                "name": household.name,
                "home": household.home_poi_id or "-",
                "members": ", ".join(member.name for member in household.members) or "-",
            }
            for household in world.households
        ]

    def handle_row(e) -> None:
        row = e.args.get("row", {}) if isinstance(e.args, dict) else {}
        household_id = row.get("id") if isinstance(row, dict) else None
        if household_id:
            hh = get_world().find_household(household_id)
            if hh:
                open_editor(hh)

    table.on("row-click", handle_row)
    ui.button("Thêm hộ", on_click=lambda: open_editor(None)).classes("mt-2")
    refresh()
