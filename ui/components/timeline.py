from __future__ import annotations

from datetime import date
from typing import Optional

from nicegui import ui

from api.models import Event
from api.services import add_event, delete_event, get_world


def timeline_view() -> None:
    table = ui.table(
        title="Sự kiện",
        columns=[
            {"name": "title", "label": "Tiêu đề", "field": "title"},
            {"name": "date", "label": "Ngày", "field": "date"},
            {"name": "tags", "label": "Tags", "field": "tags"},
            {"name": "poi", "label": "POI", "field": "poi"},
        ],
        rows=[],
        row_key="id",
    ).classes("w-full")

    def open_editor(event: Optional[Event] = None) -> None:
        dialog = ui.dialog()

        def close_and_refresh() -> None:
            dialog.close()
            refresh()

        with dialog, ui.card().classes("w-[420px]"):
            ui.label("Chỉnh sửa sự kiện" if event else "Thêm sự kiện").classes("font-semibold text-lg")
            title_input = ui.input("Tiêu đề", value=event.title if event else "")
            date_input = ui.input("Ngày (ISO)", value=event.date if event else date.today().isoformat())
            poi_input = ui.input("POI", value=event.poi_id if event else "")
            tags_input = ui.input("Tags", value=", ".join(event.tags) if event else "")
            desc_input = ui.textarea("Mô tả", value=event.description if event else "")

            def save_event() -> None:
                payload = Event(
                    id=event.id if event else None,  # type: ignore[arg-type]
                    title=title_input.value or "Sự kiện",
                    date=date_input.value or date.today().isoformat(),
                    description=desc_input.value or "",
                    poi_id=poi_input.value or None,
                    tags=[tag.strip() for tag in (tags_input.value or "").split(",") if tag.strip()],
                )
                add_event(payload)
                ui.notify("Đã lưu sự kiện", color="positive")
                close_and_refresh()

            with ui.row().classes("gap-2 mt-3"):
                ui.button("Lưu", on_click=save_event, color="primary")
                if event:
                    ui.button(
                        "Xóa", on_click=lambda: (delete_event(event.id), close_and_refresh(), ui.notify("Đã xóa", color="warning")),
                        color="negative",
                    )
                ui.button("Đóng", on_click=close_and_refresh)

        dialog.open()

    def refresh() -> None:
        world = get_world(refresh=True)
        table.rows = [
            {
                "id": event.id,
                "title": event.title,
                "date": event.date,
                "tags": ", ".join(event.tags),
                "poi": event.poi_id or "-",
            }
            for event in world.events
        ]

    def handle_row(e) -> None:
        row = e.args.get("row", {}) if isinstance(e.args, dict) else {}
        event_id = row.get("id") if isinstance(row, dict) else None
        if event_id:
            ev = next((item for item in get_world().events if item.id == event_id), None)
            if ev:
                open_editor(ev)

    table.on("row-click", handle_row)
    ui.button("Thêm sự kiện", on_click=lambda: open_editor(None)).classes("mt-2")
    refresh()
