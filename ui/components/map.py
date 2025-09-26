from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Optional

from nicegui import events, ui

from api.config import get_settings
from api.models import POI
from api.services import create_or_update_poi, delete_poi, get_world, register_media_file, set_map_image


def _storage_path(relative: Optional[str]) -> Optional[Path]:
    if not relative:
        return None
    base = get_settings().storage_dir
    return (base / relative).resolve()


def _to_data_url(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    mime = mime or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def map_view() -> None:

    with ui.card().classes("w-full"):
        ui.label("Bản đồ Thăng Long").classes("text-lg font-semibold")
        upload = ui.upload(label="Tải ảnh bản đồ", auto_upload=True).props("accept=image/*")

        @upload.on("upload")
        async def handle_upload(e: events.UploadEventArguments) -> None:
            content = await e.content.read()
            relative = register_media_file(e.name or "map.png", content)
            set_map_image(relative)
            ui.notify("Đã cập nhật bản đồ")
            refresh()

        map_container = ui.row().classes("w-full mt-4")

    poi_table = ui.table(
        title="Điểm mốc",
        columns=[
            {"name": "name", "label": "Tên", "field": "name"},
            {"name": "layer", "label": "Layer", "field": "layer"},
            {"name": "tags", "label": "Tags", "field": "tags"},
            {"name": "position", "label": "Vị trí", "field": "position"},
        ],
        rows=[],
        row_key="id",
    ).classes("w-full")

    def open_editor(poi: Optional[POI] = None) -> None:
        dialog = ui.dialog()

        def close_and_refresh() -> None:
            dialog.close()
            refresh()

        with dialog, ui.card().classes("w-[420px]"):
            ui.label("Chỉnh sửa POI" if poi else "Thêm POI").classes("font-semibold text-lg")
            name_input = ui.input("Tên", value=poi.name if poi else "")
            layer_input = ui.input("Layer", value=poi.layer if poi else "general")
            x_input = ui.number("X", value=poi.x if poi else 0.0, format="%.2f")
            y_input = ui.number("Y", value=poi.y if poi else 0.0, format="%.2f")
            tags_input = ui.input("Tags (phân tách bởi dấu phẩy)", value=", ".join(poi.tags) if poi else "")
            desc_input = ui.textarea("Mô tả", value=poi.description if poi else "")

            def save() -> None:
                payload = POI(
                    id=poi.id if poi else None,  # type: ignore[arg-type]
                    name=name_input.value or "POI",  # type: ignore[arg-type]
                    layer=layer_input.value or "general",
                    x=float(x_input.value or 0.0),
                    y=float(y_input.value or 0.0),
                    tags=[tag.strip() for tag in (tags_input.value or "").split(",") if tag.strip()],
                    description=desc_input.value or "",
                )
                create_or_update_poi(payload)
                close_and_refresh()
                ui.notify("Đã lưu POI", color="positive")

            def pick_position() -> None:
                image_path = _storage_path(get_world().map.base_image)
                if not image_path:
                    ui.notify("Hãy tải ảnh bản đồ trước", color="warning")
                    return

                picker = ui.dialog()
                with picker, ui.card():
                    ui.label("Chọn vị trí").classes("font-semibold")
                    interactive = ui.interactive_image(_to_data_url(image_path)).classes("w-[600px] h-[400px]")

                    @interactive.on("click")
                    def handle_click(event: events.GenericEventArguments) -> None:
                        coords = event.args
                        if coords:
                            x_input.value = round(coords.get("image_x", 0.0), 2)
                            y_input.value = round(coords.get("image_y", 0.0), 2)
                            picker.close()

                picker.open()

            with ui.row().classes("w-full mt-2 gap-2"):
                ui.button("Chọn trên bản đồ", on_click=pick_position)
                ui.button("Lưu", on_click=save, color="primary")
                if poi:
                    ui.button(
                        "Xóa", on_click=lambda: (delete_poi(poi.id), close_and_refresh(), ui.notify("Đã xóa", color="warning")),
                        color="negative",
                    )
                ui.button("Đóng", on_click=close_and_refresh)

        dialog.open()

    def refresh() -> None:
        map_container.clear()
        world = get_world(refresh=True)
        image_path = _storage_path(world.map.base_image)
        if image_path and image_path.exists():
            with map_container:
                ui.interactive_image(_to_data_url(image_path)).classes("w-[720px] h-[480px]")
        else:
            with map_container:
                ui.label("Chưa có ảnh bản đồ. Tải lên để bắt đầu.")

        poi_table.rows = [
            {
                "id": poi.id,
                "name": poi.name,
                "layer": poi.layer,
                "tags": ", ".join(poi.tags),
                "position": f"({poi.x:.1f}, {poi.y:.1f})",
            }
            for poi in world.pois
        ]

    def handle_row_click(e):
        row = e.args.get("row", {}) if isinstance(e.args, dict) else {}
        poi_id = row.get("id") if isinstance(row, dict) else None
        if poi_id:
            poi = get_world().find_poi(poi_id)
            if poi:
                open_editor(poi)

    poi_table.on("row-click", handle_row_click)
    ui.button("Thêm điểm mốc", on_click=lambda: open_editor(None)).classes("mt-2")
    refresh()
