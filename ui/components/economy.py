from typing import Dict, List

from nicegui import ui

from api.services import validation_summary
from api.storage import load_dataset


def economy_view() -> None:
    """Economy, trade, and faction health dashboard."""

    metrics = validation_summary()
    city = metrics.get("city_overview", {})
    trade_routes: List[Dict[str, object]] = metrics.get("trade_summary", [])  # type: ignore[assignment]
    factions: Dict[str, Dict[str, int]] = metrics.get("faction_matrix", {})  # type: ignore[assignment]
    hostility: Dict[str, Dict[str, int]] = metrics.get("hostility_matrix", {})  # type: ignore[assignment]
    festivals: List[Dict[str, object]] = load_dataset("festivals", factory=list)

    overview_card = ui.card().classes("w-full bg-slate-900 text-slate-100")
    with overview_card:
        ui.label("City Economy").classes("text-2xl font-semibold mb-2")
        with ui.grid(columns=3).classes("gap-4 w-full"):
            for label, key in (
                ("Food Required", "food_required"),
                ("Food Imported", "food_imported"),
                ("Food Balance", "food_balance"),
                ("Price Index", "price_index"),
                ("Stability", "stability"),
                ("Guard Need", "guard_need_total"),
            ):
                value = city.get(key)
                display = "-" if value is None else str(round(float(value), 2))
                with ui.card().classes("bg-slate-800 p-3"):
                    ui.label(label).classes("text-xs uppercase tracking-wide text-slate-400")
                    ui.label(display).classes("text-xl font-semibold")

    ui.separator().classes("my-4")

    ui.label("Trade Routes").classes("text-xl font-semibold text-slate-100")
    ui.table(
        columns=[
            {"name": "route", "label": "Tuyến", "field": "route"},
            {"name": "terrain", "label": "Địa hình", "field": "terrain"},
            {"name": "distance", "label": "Km", "field": "distance"},
            {"name": "sum", "label": "Tổng địa hình", "field": "sum"},
        ],
        rows=[
            {
                "route": entry.get("route_id"),
                "terrain": entry.get("dominant"),
                "distance": entry.get("distance_km"),
                "sum": entry.get("terrain_sum"),
            }
            for entry in trade_routes
        ],
        row_key="route",
    ).classes("w-full bg-slate-900 text-slate-100")

    ui.separator().classes("my-4")

    ui.label("Faction Influence").classes("text-xl font-semibold text-slate-100")
    with ui.row().classes("gap-4 flex-wrap"):
        for faction, presence in factions.items():
            with ui.card().classes("bg-slate-900 text-slate-100 p-3 min-w-[220px]"):
                ui.label(faction).classes("font-semibold")
                for district, value in sorted(presence.items()):
                    ui.label(f"{district}: {value}")

    if hostility:
        ui.separator().classes("my-4")
        ui.label("Hostility Matrix").classes("text-xl font-semibold text-slate-100")
        for faction, targets in hostility.items():
            ui.label(f"{faction} → {', '.join(f'{k}:{v}' for k, v in sorted(targets.items()))}").classes("text-slate-200")

    if festivals:
        ui.separator().classes("my-4")
        ui.label("Festival Schedule").classes("text-xl font-semibold text-slate-100")
        ui.table(
            columns=[
                {"name": "name", "label": "Lễ hội", "field": "name"},
                {"name": "date", "label": "Ngày", "field": "date"},
                {"name": "zone", "label": "Khu vực", "field": "zone"},
                {"name": "effects", "label": "Tác động", "field": "effects"},
            ],
            rows=[
                {
                    "name": festival.get("name"),
                    "date": f"Th {festival.get('month')} / Ng {festival.get('day')}",
                    "zone": festival.get("primary_zone"),
                    "effects": ", ".join(
                        filter(
                            None,
                            [
                                f"Vendor +{effects.get('vendor_boost_pct', 0)*100:.0f}%" if effects else None,
                                f"Guard {effects.get('guard_shift', 0)*100:.0f}%" if effects else None,
                                f"Crime {effects.get('crime_shift', 0)*100:.0f}%" if effects else None,
                            ],
                        )
                    ),
                }
                for festival in festivals
                for effects in [festival.get("effects", {})]
            ],
            row_key="name",
        ).classes("w-full bg-slate-900 text-slate-100")

