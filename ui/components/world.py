from typing import Any, Dict, List

from nicegui import ui

from api.config import settings_summary
from api.services import regenerate_foundation, validation_summary


def _format_hostility(matrix: Dict[str, Dict[str, int]]) -> List[str]:
    lines: List[str] = []
    for faction, opponents in matrix.items():
        parts = ", ".join(f"{target}:{score}" for target, score in sorted(opponents.items()))
        lines.append(f"{faction} → {parts}")
    return lines


def world_view() -> None:
    """High-level dashboard of current datasets and health metrics."""

    summary_card = ui.card().classes("w-full bg-slate-900 text-slate-100")
    detail_card = ui.card().classes("w-full bg-slate-900 text-slate-100")
    settings_card = ui.card().classes("w-full bg-slate-900 text-slate-200")

    def refresh() -> None:
        metrics = validation_summary()
        counts: Dict[str, Any] = metrics.get("dataset_counts", {})
        city_overview: Dict[str, Any] = metrics.get("city_overview", {})
        district_snapshots: Dict[str, Dict[str, Any]] = metrics.get("districts", {})
        coverage_matrix: Dict[str, Dict[str, Any]] = metrics.get("coverage_matrix", {})
        trade_summary: List[Dict[str, Any]] = metrics.get("trade_summary", [])
        faction_matrix: Dict[str, Dict[str, int]] = metrics.get("faction_matrix", {})
        hostility_matrix: Dict[str, Dict[str, int]] = metrics.get("hostility_matrix", {})

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
            if city_overview:
                ui.separator()
                with ui.grid(columns=3).classes("gap-4 w-full"):
                    for label, key in (
                        ("Dân số mục tiêu", "population_target"),
                        ("Lương thực cần", "food_required"),
                        ("Lương thực nhập", "food_imported"),
                        ("Cân bằng", "food_balance"),
                        ("Chỉ số giá", "price_index"),
                        ("Ổn định", "stability"),
                    ):
                        value = city_overview.get(key)
                        with ui.card().classes("bg-slate-800 text-slate-100 p-3"):
                            ui.label(label).classes("uppercase text-xs tracking-wide text-slate-400")
                            ui.label(f"{value}").classes("text-lg font-semibold")
            ui.separator()
            with ui.row().classes("gap-4 flex-wrap"):
                for key, value in sorted(counts.items()):
                    with ui.card().classes("bg-slate-800 p-3 min-w-[160px]"):
                        ui.label(key.upper()).classes("text-xs text-slate-400")
                        ui.label(str(value)).classes("text-2xl font-semibold")
            if metrics["issues"]:
                with ui.expansion(f"⚠️ {metrics['issues']} rule violations", icon="warning").classes("w-full"):
                    for issue in metrics["issue_messages"]:
                        ui.label(issue)
            else:
                ui.label("✅ All rule checks passed").classes("text-emerald-400")

        detail_card.clear()
        with detail_card:
            ui.label("City Systems").classes("text-xl font-semibold mb-2")
            if district_snapshots:
                ui.label("District Health").classes("text-sm text-slate-400")
                ui.table(
                    columns=[
                        {"name": "district", "label": "Quận", "field": "district"},
                        {"name": "population", "label": "Dân số", "field": "population"},
                        {"name": "crime", "label": "Tội phạm", "field": "crime"},
                        {"name": "guard", "label": "Canh phòng", "field": "guard"},
                        {"name": "capacity", "label": "Sức chứa", "field": "capacity"},
                    ],
                    rows=[
                        {
                            "district": district,
                            "population": snapshot.get("population"),
                            "crime": snapshot.get("crime_expected"),
                            "guard": snapshot.get("guard_coverage"),
                            "capacity": f"{snapshot.get('capacity')}/{snapshot.get('capacity_target')}",
                        }
                        for district, snapshot in district_snapshots.items()
                    ],
                ).classes("w-full mb-4")
            if coverage_matrix:
                ui.label("Coverage Matrix (Quest/Vendor/Guard/Event)").classes("text-sm text-slate-400 mt-2")
                ui.table(
                    columns=[
                        {"name": "district", "label": "Quận", "field": "district"},
                        {"name": "quests", "label": "Quest", "field": "quests"},
                        {"name": "vendors", "label": "Vendor", "field": "vendors"},
                        {"name": "guard", "label": "Guard OK", "field": "guard"},
                        {"name": "events", "label": "Sự kiện", "field": "events"},
                    ],
                    rows=[
                        {
                            "district": district,
                            "quests": snapshot.get("quests"),
                            "vendors": snapshot.get("vendors"),
                            "guard": "✅" if snapshot.get("guard_ready") else "⚠️",
                            "events": snapshot.get("events"),
                        }
                        for district, snapshot in coverage_matrix.items()
                    ],
                ).classes("w-full mb-4")
            if trade_summary:
                ui.label("Trade Routes").classes("text-sm text-slate-400 mt-2")
                ui.table(
                    columns=[
                        {"name": "route_id", "label": "Tuyến", "field": "route_id"},
                        {"name": "dominant", "label": "Địa hình", "field": "dominant"},
                        {"name": "distance", "label": "Km", "field": "distance"},
                        {"name": "terrain", "label": "Tổng địa hình", "field": "terrain"},
                    ],
                    rows=[
                        {
                            "route_id": entry.get("route_id"),
                            "dominant": entry.get("dominant"),
                            "distance": entry.get("distance_km"),
                            "terrain": entry.get("terrain_sum"),
                        }
                        for entry in trade_summary
                    ],
                ).classes("w-full mb-4")
            if faction_matrix:
                ui.label("Faction Influence").classes("text-sm text-slate-400 mt-2")
                with ui.row().classes("gap-4 flex-wrap"):
                    for faction, districts in faction_matrix.items():
                        with ui.card().classes("bg-slate-800 p-3 min-w-[200px]"):
                            ui.label(faction).classes("font-semibold")
                            for district, value in sorted(districts.items()):
                                ui.label(f"{district}: {value}")
            if hostility_matrix:
                ui.label("Faction Hostility").classes("text-sm text-slate-400 mt-4")
                for line in _format_hostility(hostility_matrix):
                    ui.label(line)

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

