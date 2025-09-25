from __future__ import annotations

from nicegui import ui

from api.services import export_bundle, list_available_exports, validation_summary


EXPORTABLE_TYPES = [
    "pois",
    "households",
    "persons",
    "events",
    "quests",
    "story_arcs",
    "monster_zones",
    "features",
    "items",
    "activities",
]


def qa_view() -> None:
    """Exporter & QA hub with rulebook insights."""

    with ui.row().classes("gap-4 items-end"):
        formats = ui.select(["json", "csv", "unity"], value="json", label="Định dạng")
        types = ui.select(
            EXPORTABLE_TYPES,
            value=["pois", "households", "persons", "events"],
            label="Loại dữ liệu",
            multiple=True,
        ).classes("min-w-[220px]")

        def trigger_export() -> None:
            path = export_bundle(types.value, fmt=formats.value)
            refresh_exports()
            ui.notify(f"Đã xuất dữ liệu → {path}")

        ui.button("Export", on_click=trigger_export)

    issue_card = ui.card().classes("w-full bg-slate-900 text-slate-100")
    export_table = ui.table(
        columns=[{"name": "path", "label": "File", "field": "path"}],
        rows=[],
        row_key="path",
    ).classes("w-full")

    def refresh_issues() -> None:
        metrics = validation_summary()
        issue_card.clear()
        with issue_card:
            ui.label("Rulebook Violations").classes("text-xl font-semibold mb-2")
            if not metrics["issues"]:
                ui.label("Không có lỗi phát hiện").classes("text-emerald-400")
            else:
                for issue in metrics["issue_messages"]:
                    ui.label(f"• {issue}")
            ui.separator()
            ui.label("Encounter Variety Breakdown").classes("text-sm text-slate-400")
            for style, value in metrics.get("encounter_breakdown", {}).items():
                with ui.row().classes("items-center gap-2"):
                    ui.label(style.capitalize()).classes("w-24")
                    ui.linear_progress(value=float(value) / 100.0).props("color=cyan")
                    ui.label(f"{value}%").classes("text-sm")
            ui.label("Loot Distribution").classes("text-sm text-slate-400 mt-4")
            for source, value in metrics.get("loot_distribution", {}).items():
                ui.label(f"{source}: {value}%")

    def refresh_exports() -> None:
        export_table.rows = [{"path": str(path)} for path in list_available_exports()]

    refresh_issues()
    refresh_exports()
