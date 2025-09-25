from __future__ import annotations

from typing import List

from nicegui import ui

from api.models import GameplayFeature, MonsterZone
from api.services import generate_gameplay_features, generate_monster_zones
from api.storage import load_dataset


def _load_zones() -> List[MonsterZone]:
    return [MonsterZone.model_validate(item) for item in load_dataset("monster_zones", factory=list)]


def _load_features() -> List[GameplayFeature]:
    return [GameplayFeature.model_validate(item) for item in load_dataset("features", factory=list)]


def encounters_view() -> None:
    """Map & encounter planning overlays."""

    with ui.row().classes("gap-4 items-end"):
        seed_input = ui.number("Seed", value=42, min=0).classes("w-32")

        def regenerate() -> None:
            generate_monster_zones(seed=int(seed_input.value or 0))
            generate_gameplay_features(seed=int(seed_input.value or 0))
            refresh_tables()
            ui.notify("Đã làm mới monster zone và feature placement")

        ui.button("Refresh encounters", on_click=regenerate).classes("bg-indigo-500 text-white")

    zone_table = ui.table(
        columns=[
            {"name": "zone_id", "label": "Zone", "field": "zone_id"},
            {"name": "name", "label": "Tên", "field": "name"},
            {"name": "faction", "label": "Faction", "field": "faction"},
            {"name": "level", "label": "Cấp độ", "field": "level"},
            {"name": "styles", "label": "Variety", "field": "styles"},
        ],
        rows=[],
        row_key="zone_id",
    ).classes("w-full shadow-lg")

    feature_table = ui.table(
        columns=[
            {"name": "feature_id", "label": "Feature", "field": "feature_id"},
            {"name": "type", "label": "Loại", "field": "type"},
            {"name": "poi", "label": "POI", "field": "poi"},
            {"name": "unlock", "label": "Điều kiện", "field": "unlock"},
        ],
        rows=[],
        row_key="feature_id",
    ).classes("w-full shadow-lg")

    def refresh_tables() -> None:
        zones = _load_zones()
        features = _load_features()
        zone_table.rows = [
            {
                "zone_id": zone.zone_id,
                "name": zone.name,
                "faction": zone.faction,
                "level": f"{zone.level_range[0]}-{zone.level_range[1]}",
                "styles": ", ".join(sorted({enc.style for enc in zone.encounters})),
            }
            for zone in zones
        ]
        feature_table.rows = [
            {
                "feature_id": feature.feature_id,
                "type": feature.feature_type,
                "poi": feature.poi_id,
                "unlock": feature.unlock_condition,
            }
            for feature in features
        ]

    refresh_tables()

