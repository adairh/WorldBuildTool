from __future__ import annotations

from typing import List

from nicegui import ui

from api.models import Activity, Event
from api.services import generate_timeline
from api.storage import load_dataset


def _load_events() -> List[Event]:
    return [Event.model_validate(item) for item in load_dataset("events", factory=list)]


def _load_activities() -> List[Activity]:
    return [Activity.model_validate(item) for item in load_dataset("activities", factory=list)]


def timeline_view() -> None:
    """Timeline & Simulation pillar."""

    with ui.row().classes("gap-4 items-end"):
        day_input = ui.number("Số ngày", value=7, min=1, max=120).classes("w-40")
        seed_input = ui.number("Seed", value=42, min=0).classes("w-40")

        def trigger() -> None:
            generate_timeline(int(day_input.value or 7), seed=int(seed_input.value or 0))
            refresh_table()
            ui.notify("Đã sinh timeline")

        ui.button("Generate", on_click=trigger)

    event_table = ui.table(
        columns=[
            {"name": "event_id", "label": "ID", "field": "event_id"},
            {"name": "date", "label": "Ngày", "field": "date"},
            {"name": "title", "label": "Tiêu đề", "field": "title"},
            {"name": "links", "label": "Liên kết", "field": "links"},
        ],
        rows=[],
        row_key="event_id",
    ).classes("w-full")

    activity_table = ui.table(
        columns=[
            {"name": "activity_id", "label": "Activity", "field": "activity_id"},
            {"name": "cadence", "label": "Chu kỳ", "field": "cadence"},
            {"name": "schedule", "label": "Lịch", "field": "schedule"},
        ],
        rows=[],
        row_key="activity_id",
    ).classes("w-full mt-6")

    def refresh_table() -> None:
        events = _load_events()
        activities = _load_activities()
        event_table.rows = [
            {
                "event_id": event.event_id,
                "date": event.date.isoformat(),
                "title": event.title,
                "links": f"POIs: {', '.join(event.linked_poi_ids) or '-'} | NPCs: {', '.join(event.linked_person_ids) or '-'}",
            }
            for event in events
        ]
        activity_table.rows = [
            {
                "activity_id": activity.activity_id,
                "cadence": activity.schedule.cadence,
                "schedule": f"Days: {', '.join(activity.schedule.days)} | Seasons: {', '.join(activity.schedule.seasons)}",
            }
            for activity in activities
        ]

    refresh_table()
