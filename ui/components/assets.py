from __future__ import annotations

from typing import Optional

from nicegui import ui

from api.models import Asset
from api.services import add_asset, delete_asset, get_world


def asset_view() -> None:
    table = ui.table(
        title="Tài nguyên",
        columns=[
            {"name": "name", "label": "Tên", "field": "name"},
            {"name": "kind", "label": "Loại", "field": "kind"},
            {"name": "status", "label": "Trạng thái", "field": "status"},
            {"name": "owner", "label": "Owner", "field": "owner"},
        ],
        rows=[],
        row_key="id",
    ).classes("w-full")

    def open_editor(asset: Optional[Asset] = None) -> None:
        dialog = ui.dialog()

        def close_and_refresh() -> None:
            dialog.close()
            refresh()

        with dialog, ui.card().classes("w-[420px]"):
            ui.label("Chỉnh sửa tài nguyên" if asset else "Thêm tài nguyên").classes("font-semibold text-lg")
            name_input = ui.input("Tên", value=asset.name if asset else "")
            kind_input = ui.input("Loại", value=asset.kind if asset else "concept")
            status_input = ui.input("Trạng thái", value=asset.status if asset else "draft")
            owner_input = ui.input("Owner", value=asset.owner if asset else "designer")
            tags_input = ui.input("Tags", value=", ".join(asset.tags) if asset else "")
            notes_input = ui.textarea("Ghi chú", value=asset.notes if asset else "")
            ref_input = ui.input("Reference", value=asset.reference if asset else "")

            def save_asset() -> None:
                payload = Asset(
                    id=asset.id if asset else None,  # type: ignore[arg-type]
                    name=name_input.value or "Tài nguyên",
                    kind=kind_input.value or "concept",
                    status=status_input.value or "draft",
                    owner=owner_input.value or "designer",
                    tags=[tag.strip() for tag in (tags_input.value or "").split(",") if tag.strip()],
                    notes=notes_input.value or "",
                    reference=ref_input.value or None,
                )
                add_asset(payload)
                ui.notify("Đã lưu", color="positive")
                close_and_refresh()

            with ui.row().classes("gap-2 mt-3"):
                ui.button("Lưu", on_click=save_asset, color="primary")
                if asset:
                    ui.button(
                        "Xóa", on_click=lambda: (delete_asset(asset.id), close_and_refresh(), ui.notify("Đã xóa", color="warning")),
                        color="negative",
                    )
                ui.button("Đóng", on_click=close_and_refresh)

        dialog.open()

    def refresh() -> None:
        world = get_world(refresh=True)
        table.rows = [
            {
                "id": asset.id,
                "name": asset.name,
                "kind": asset.kind,
                "status": asset.status,
                "owner": asset.owner,
            }
            for asset in world.assets
        ]

    def handle_row(e) -> None:
        row = e.args.get("row", {}) if isinstance(e.args, dict) else {}
        asset_id = row.get("id") if isinstance(row, dict) else None
        if asset_id:
            asset = next((item for item in get_world().assets if item.id == asset_id), None)
            if asset:
                open_editor(asset)

    table.on("row-click", handle_row)
    ui.button("Thêm tài nguyên", on_click=lambda: open_editor(None)).classes("mt-2")
    refresh()
