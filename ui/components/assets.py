from __future__ import annotations

from nicegui import ui

from api.services import export_bundle, list_available_exports, validate_world


def asset_view() -> None:
    """Exporter & Consistency tools."""

    with ui.row().classes("gap-4 items-end"):
        formats = ui.select(["json", "csv", "unity"], value="json", label="Định dạng")
        types = ui.select(
            ["pois", "households", "persons", "events"],
            value=["pois", "households", "persons", "events"],
            label="Loại dữ liệu",
            multiple=True,
        ).classes("min-w-[220px]")

        def trigger_export() -> None:
            path = export_bundle(types.value, fmt=formats.value)
            refresh_exports()
            ui.notify(f"Đã xuất dữ liệu → {path}")

        ui.button("Export", on_click=trigger_export)

    issue_card = ui.card().classes("w-full")
    export_table = ui.table(
        columns=[{"name": "path", "label": "File", "field": "path"}],
        rows=[],
        row_key="path",
    ).classes("w-full")

    def refresh_issues() -> None:
        issues = validate_world()
        issue_card.clear()
        with issue_card:
            ui.label("Consistency Checker").classes("text-xl font-semibold")
            if not issues:
                ui.label("Không có lỗi phát hiện").classes("text-green-600")
            else:
                for issue in issues:
                    ui.label(issue)

    def refresh_exports() -> None:
        export_table.rows = [{"path": str(path)} for path in list_available_exports()]

    refresh_issues()
    refresh_exports()
