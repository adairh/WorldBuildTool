from __future__ import annotations

import json
from typing import List, Optional

from nicegui import ui

from api.models import POI
from api.services import delete_poi, generate_poi, list_pois, update_poi, validation_summary

try:  # optional dependency for interactive map
    import leafmap  # type: ignore
    from ipywidgets import HTML  # type: ignore
except Exception:  # pragma: no cover - optional dependency missing
    leafmap = None
    HTML = None  # type: ignore


def _parse_csv(text: Optional[str]) -> List[str]:
    return [item.strip() for item in (text or "").split(",") if item.strip()]


def _format_csv(values: List[str]) -> str:
    return ", ".join(values)


def _load_pois() -> List[POI]:
    return list_pois()


def map_view() -> None:
    """Map & Spatial pillar overview with full POI control."""

    summary = validation_summary()

    with ui.grid(columns=3).classes("gap-4 w-full"):
        for label, key in (
            ("Story Coverage", "story_coverage"),
            ("Monster Variety", "monster_variety"),
            ("Feature Coverage", "feature_coverage"),
        ):
            value = float(summary.get(key, 0)) / 100.0
            with ui.card().classes("bg-slate-900 text-slate-100 p-4"):
                ui.label(label).classes("uppercase text-xs tracking-wide text-slate-400")
                ui.label(f"{summary.get(key, 0)} %").classes("text-xl font-semibold")
                ui.linear_progress(value=value).props("color=amber")

    selection_state: dict[str, Optional[str]] = {"id": None}

    with ui.row().classes("gap-6 w-full items-start"):
        left_column = ui.column().classes("flex-1 gap-4")
        with left_column:
            with ui.card().classes("p-4 gap-3"):
                ui.label("Thêm địa điểm mới").classes("font-semibold text-lg")
                with ui.row().classes("gap-3 flex-wrap"):
                    name_input = ui.input("Tên POI").classes("w-48")
                    layer_input = ui.input("Layers (phân tách bằng dấu phẩy)").classes("w-60")
                    tag_input = ui.input("Tags").classes("w-52")
                with ui.row().classes("gap-3 flex-wrap"):
                    lon_input = ui.number("Kinh độ", step=0.0001).classes("w-40")
                    lat_input = ui.number("Vĩ độ", step=0.0001).classes("w-40")
                    kind_input = ui.input("Loại").classes("w-40")
                description_input = ui.textarea("Mô tả").props("rows=2").classes("w-full")

                def handle_create() -> None:
                    try:
                        coords = None
                        if lon_input.value is not None and lat_input.value is not None:
                            coords = [float(lon_input.value), float(lat_input.value)]
                        poi = generate_poi(
                            name_input.value or "POI mới",
                            layers=_parse_csv(layer_input.value),
                            tags=_parse_csv(tag_input.value),
                            coordinates=coords,
                            description=description_input.value or "",
                            kind=kind_input.value or "landmark",
                        )
                        selection_state["id"] = poi.id
                        refresh()
                        ui.notify(f"Đã tạo POI '{poi.properties.name}'")
                        name_input.value = ""
                        layer_input.value = ""
                        tag_input.value = ""
                        description_input.value = ""
                        lon_input.value = None
                        lat_input.value = None
                        kind_input.value = ""
                    except Exception as exc:  # pragma: no cover - user input errors
                        ui.notify(f"Không thể tạo POI: {exc}", color="negative")

                ui.button("Thêm POI", on_click=handle_create)

            with ui.card().classes("p-4 gap-3"):
                ui.label("Chỉnh sửa địa điểm").classes("font-semibold text-lg")
                select_input = ui.select(options=[], label="Chọn POI").classes("w-full")
                edit_name = ui.input("Tên").classes("w-full")
                edit_kind = ui.input("Loại").classes("w-full")
                edit_layers = ui.input("Layers (phân tách bằng dấu phẩy)").classes("w-full")
                edit_tags = ui.input("Tags").classes("w-full")
                edit_media = ui.input("Media (URL, phân tách bằng dấu phẩy)").classes("w-full")
                edit_lon = ui.number("Kinh độ", step=0.0001).classes("w-40")
                edit_lat = ui.number("Vĩ độ", step=0.0001).classes("w-40")
                edit_description = ui.textarea("Mô tả").props("rows=3").classes("w-full")

                def populate_form(poi: Optional[POI]) -> None:
                    if poi is None:
                        edit_name.value = ""
                        edit_kind.value = ""
                        edit_layers.value = ""
                        edit_tags.value = ""
                        edit_media.value = ""
                        edit_lon.value = None
                        edit_lat.value = None
                        edit_description.value = ""
                        return
                    edit_name.value = poi.properties.name
                    edit_kind.value = poi.properties.kind
                    edit_layers.value = _format_csv(poi.properties.layers)
                    edit_tags.value = _format_csv(poi.properties.tags)
                    edit_media.value = _format_csv(poi.properties.media)
                    edit_lon.value = poi.geometry.coordinates[0]
                    edit_lat.value = poi.geometry.coordinates[1]
                    edit_description.value = poi.properties.description

                def handle_selection(value: Optional[str]) -> None:
                    selection_state["id"] = value
                    pois = _load_pois()
                    match = next((poi for poi in pois if poi.id == value), None)
                    populate_form(match)

                select_input.on_value_change(lambda e: handle_selection(e.value))

                def handle_update() -> None:
                    poi_id = selection_state["id"]
                    if not poi_id:
                        ui.notify("Chưa chọn địa điểm để cập nhật", color="warning")
                        return
                    try:
                        coords = None
                        if edit_lon.value is not None and edit_lat.value is not None:
                            coords = [float(edit_lon.value), float(edit_lat.value)]
                        update_poi(
                            poi_id,
                            name=edit_name.value or "POI không tên",
                            kind=edit_kind.value or "landmark",
                            layers=_parse_csv(edit_layers.value),
                            tags=_parse_csv(edit_tags.value),
                            media=_parse_csv(edit_media.value),
                            description=edit_description.value or "",
                            coordinates=coords,
                        )
                        refresh()
                        ui.notify("Đã cập nhật địa điểm")
                    except ValueError as exc:
                        ui.notify(str(exc), color="negative")

                def handle_delete() -> None:
                    poi_id = selection_state["id"]
                    if not poi_id:
                        ui.notify("Chưa chọn địa điểm để xóa", color="warning")
                        return
                    try:
                        delete_poi(poi_id)
                        selection_state["id"] = None
                        refresh()
                        ui.notify("Đã xóa địa điểm")
                    except ValueError as exc:
                        ui.notify(str(exc), color="negative")

                with ui.row().classes("gap-3"):
                    ui.button("Lưu thay đổi", on_click=handle_update)
                    ui.button("Xóa địa điểm", on_click=handle_delete).props("color=negative")

            poi_table = ui.table(
                columns=[
                    {"name": "id", "label": "ID", "field": "id"},
                    {"name": "name", "label": "Tên", "field": "name"},
                    {"name": "kind", "label": "Loại", "field": "kind"},
                    {"name": "layers", "label": "Layers", "field": "layers"},
                    {"name": "tags", "label": "Tags", "field": "tags"},
                ],
                rows=[],
                row_key="id",
            ).classes("w-full")
        map_column = ui.column().classes("w-[40%] gap-4")

    def render_map(pois: List[POI]) -> None:
        map_column.clear()
        with map_column:
            if leafmap is None:
                ui.label(
                    "Leafmap chưa sẵn sàng. Vui lòng cài 'leafmap' và 'ipywidgets' để xem bản đồ trực quan."
                ).classes("text-sm text-gray-400")
            else:
                geo = leafmap.Map(center=[21.0285, 105.8542], zoom=12)
                for poi in pois:
                    lat, lon = poi.geometry.coordinates[1], poi.geometry.coordinates[0]
                    overlay = ", ".join(poi.properties.layers)
                    popup_text = poi.properties.name
                    if overlay:
                        popup_text += f" — {overlay}"
                    if HTML is not None:  # ipywidgets available
                        popup_widget = HTML(value=f"<strong>{popup_text}</strong>")
                    else:  # pragma: no cover - safety fallback
                        popup_widget = None
                    geo.add_marker([lat, lon], popup=popup_widget)
                map_html = geo.to_html()
                ui.element("iframe").style(
                    "width: 100%; height: 26rem; border: 1px solid #1e293b; border-radius: 0.75rem;"
                ).props(f"srcdoc={json.dumps(map_html)}")

    def refresh() -> None:
        pois = _load_pois()
        poi_table.rows = [
            {
                "id": poi.id,
                "name": poi.properties.name,
                "kind": poi.properties.kind,
                "layers": _format_csv(poi.properties.layers) or "(none)",
                "tags": _format_csv(poi.properties.tags) or "(none)",
            }
            for poi in pois
        ]
        options = [
            {"label": f"{poi.properties.name} ({poi.id})", "value": poi.id}
            for poi in pois
        ]
        select_input.options = options
        if selection_state["id"] and selection_state["id"] not in {opt["value"] for opt in options}:
            selection_state["id"] = None
        if selection_state["id"] is None and options:
            selection_state["id"] = options[0]["value"]
        select_input.value = selection_state["id"]
        match = next((poi for poi in pois if poi.id == selection_state["id"]), None)
        populate_form(match)

        render_map(pois)

    def on_startup() -> None:
        refresh()

    ui.on_startup(on_startup)
    refresh()
