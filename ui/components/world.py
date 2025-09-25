from __future__ import annotations

from typing import Dict

from nicegui import ui

from api.config import settings_summary
from api.services import regenerate_foundation, validation_summary
from api.storage import load_dataset


def _count_items() -> Dict[str, int]:
    return {
        "pois": len(load_dataset("pois", factory=list)),
        "households": len(load_dataset("households", factory=list)),
        "persons": len(load_dataset("persons", factory=list)),
        "events": len(load_dataset("events", factory=list)),
    }


def world_view() -> None:
    """High-level dashboard of current datasets."""

    summary_card = ui.card().classes("w-full bg-slate-900 text-slate-100")
    settings_card = ui.card().classes("w-full bg-slate-900 text-slate-200")

    def refresh() -> None:
        counts = _count_items()
        metrics = validation_summary()
        summary_card.clear()
        with summary_card:
            ui.label("Command Desk").classes("text-2xl font-bold mb-2")
            with ui.grid(columns=3).classes("gap-4 w-full"):
                for label, key in (
                    ("Story Coverage", "story_coverage"),
                    ("Feature Coverage", "feature_coverage"),
                    ("Activity Coverage", "activity_coverage"),
                    ("Monster Variety", "monster_variety"),
                    ("Loot Health", "loot_health"),
                    ("Export Readiness", "export_ready"),
                ):
                    value = float(metrics.get(key, 0)) / 100.0
                    with ui.card().classes("bg-slate-800 text-slate-100 p-4"):
                        ui.label(label).classes("uppercase text-xs tracking-wide text-slate-400")
                        ui.label(f"{metrics.get(key, 0)} %").classes("text-xl font-semibold")
                        ui.linear_progress(value=value).props("color=teal")
            ui.separator()
            with ui.row().classes("gap-4 flex-wrap"):
                for key, value in counts.items():
                    with ui.card().classes("bg-slate-800 p-3 min-w-[160px]"):
                        ui.label(key.upper()).classes("text-xs text-slate-400")
                        ui.label(str(value)).classes("text-2xl font-semibold")
            if metrics["issues"]:
                with ui.expansion(f"⚠️ {metrics['issues']} rule violations", icon="warning").classes("w-full"):
                    for issue in metrics["issue_messages"]:
                        ui.label(issue)
            else:
                ui.label("✅ All rule checks passed").classes("text-emerald-400")

        settings_card.clear()
        with settings_card:
            ui.label("Storage & Schedule").classes("text-xl font-semibold mb-2")
            for key, value in settings_summary().items():
                ui.label(f"{key}: {value}")
            schedule = metrics.get("schedule_overview", {})
            if schedule:
                ui.label("Activity Cadence").classes("text-sm text-slate-400 mt-4")
                for cadence, names in schedule.items():
                    ui.label(f"{cadence}: {', '.join(names)}")

    def reset_data() -> None:
        regenerate_foundation()
        refresh()
        ui.notify("Đã tạo bộ dữ liệu nền cho Thăng Long")

    ui.button("Regenerate Foundation", on_click=reset_data).classes("bg-rose-500 text-white")
    refresh()
