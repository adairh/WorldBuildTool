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

    summary_card = ui.card().classes("w-full")
    settings_card = ui.card().classes("w-full")

    def refresh() -> None:
        counts = _count_items()
        summary_card.clear()
        with summary_card:
            ui.label("Dataset Overview").classes("text-xl font-semibold")
            with ui.row().classes("gap-4 flex-wrap"):
                for key, value in counts.items():
                    with ui.card().classes("p-3 min-w-[160px]"):
                        ui.label(key.upper()).classes("text-sm text-gray-500")
                        ui.label(str(value)).classes("text-2xl font-bold")
            issues = validation_summary()["issues"]
            if issues:
                ui.label(f"⚠️ {issues} vấn đề cần xử lý").classes("text-red-600")
            else:
                ui.label("✅ Không phát hiện lỗi nhất quán").classes("text-green-600")

        settings_card.clear()
        with settings_card:
            ui.label("Storage").classes("text-xl font-semibold")
            for key, value in settings_summary().items():
                ui.label(f"{key}: {value}")

    def reset_data() -> None:
        regenerate_foundation()
        refresh()
        ui.notify("Đã tạo bộ dữ liệu nền cho Thăng Long")

    ui.button("Regenerate Foundation", on_click=reset_data)
    refresh()
