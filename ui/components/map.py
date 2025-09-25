from __future__ import annotations

import json
from typing import List

from nicegui import ui

from api.models import POI
from api.services import generate_poi, validation_summary
from api.storage import load_dataset

try:  # optional dependency for interactive map
    import leafmap  # type: ignore
except Exception:  # pragma: no cover - optional dependency missing
    leafmap = None


def _load_pois() -> List[POI]:
    return [POI.model_validate(item) for item in load_dataset("pois", factory=list)]


def map_view() -> None:
    """Map & Spatial pillar overview."""

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

    poi_table = ui.table(
        columns=[
            {"name": "id", "label": "ID", "field": "id"},
            {"name": "name", "label": "Tên", "field": "name"},
            {"name": "layers", "label": "Layers", "field": "layers"},
            {"name": "tags", "label": "Tags", "field": "tags"},
        ],
        rows=[],
        row_key="id",
    ).classes("w-full")

    def refresh_table() -> None:
        rows = []
        for poi in _load_pois():
            rows.append(
                {
                    "id": poi.id,
                    "name": poi.properties.name,
                    "layers": ", ".join(poi.properties.layers) or "(none)",
                    "tags": ", ".join(poi.properties.tags) or "(none)",
                }
            )
        poi_table.rows = rows

    def handle_create(name: str, layers: str, tags: str) -> None:
        layer_list = [item.strip() for item in layers.split(",") if item.strip()]
        tag_list = [item.strip() for item in tags.split(",") if item.strip()]
        generate_poi(name, layers=layer_list, tags=tag_list)
        refresh_table()
        ui.notify(f"Đã tạo POI '{name}'")

    with ui.row().classes("gap-4 items-end"):
        name_input = ui.input("Tên POI").classes("w-40")
        layer_input = ui.input("Layers (phân tách bằng dấu phẩy)").classes("w-60")
        tag_input = ui.input("Tags").classes("w-60")
        ui.button(
            "Thêm POI",
            on_click=lambda: handle_create(
                name_input.value or "POI mới",
                layer_input.value or "",
                tag_input.value or "",
            ),
        )

    if leafmap is None:
        ui.label("Leafmap chưa cài đặt; hiển thị danh sách POI dạng bảng.").classes("text-sm text-gray-400")
    else:
        geo = leafmap.Map(center=[21.0285, 105.8542], zoom=12)
        for poi in _load_pois():
            lat, lon = poi.geometry.coordinates[1], poi.geometry.coordinates[0]
            overlay = ", ".join(poi.properties.layers)
            geo.add_marker([lat, lon], popup=f"{poi.properties.name} — {overlay}")
        map_html = geo.to_html()
        ui.element("iframe").style(
            "width: 100%; height: 24rem; border: 1px solid #1e293b; border-radius: 0.75rem;"
        ).props(f"srcdoc={json.dumps(map_html)}")

    refresh_table()
