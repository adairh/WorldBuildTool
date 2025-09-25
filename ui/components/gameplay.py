from __future__ import annotations

from typing import List

from nicegui import ui

from api.models import Activity, GameplayFeature
from api.services import generate_activities
from api.storage import load_dataset


def _load_activities() -> List[Activity]:
    return [Activity.model_validate(item) for item in load_dataset("activities", factory=list)]


def _load_features() -> List[GameplayFeature]:
    return [GameplayFeature.model_validate(item) for item in load_dataset("features", factory=list)]


def gameplay_view() -> None:
    """Gameplay systems coverage: features, activities, schedules."""

    with ui.row().classes("gap-4 items-end"):
        seed_input = ui.number("Seed", value=42, min=0).classes("w-32")

        def regenerate() -> None:
            generate_activities(seed=int(seed_input.value or 0))
            refresh_tables()
            ui.notify("Đã cập nhật hoạt động và lịch diễn ra")

        ui.button("Refresh schedule", on_click=regenerate).classes("bg-amber-500 text-white")

    feature_table = ui.table(
        columns=[
            {"name": "feature_id", "label": "Feature", "field": "feature_id"},
            {"name": "type", "label": "Loại", "field": "type"},
            {"name": "unlock", "label": "Điều kiện", "field": "unlock"},
            {"name": "group", "label": "Co-op", "field": "group"},
        ],
        rows=[],
        row_key="feature_id",
    ).classes("w-full shadow-lg")

    activity_table = ui.table(
        columns=[
            {"name": "activity_id", "label": "Activity", "field": "activity_id"},
            {"name": "name", "label": "Tên", "field": "name"},
            {"name": "cadence", "label": "Chu kỳ", "field": "cadence"},
            {"name": "rewards", "label": "Phần thưởng", "field": "rewards"},
        ],
        rows=[],
        row_key="activity_id",
    ).classes("w-full shadow-lg")

    def refresh_tables() -> None:
        features = _load_features()
        activities = _load_activities()
        feature_table.rows = [
            {
                "feature_id": feature.feature_id,
                "type": feature.feature_type,
                "unlock": feature.unlock_condition,
                "group": "Có" if feature.supports_groups else "Không",
            }
            for feature in features
        ]
        activity_table.rows = [
            {
                "activity_id": activity.activity_id,
                "name": activity.name,
                "cadence": f"{activity.schedule.cadence} | {'/'.join(activity.schedule.seasons)}",
                "rewards": ", ".join(activity.rewards),
            }
            for activity in activities
        ]

    refresh_tables()

