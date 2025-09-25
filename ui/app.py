from __future__ import annotations

from nicegui import ui

from .components.assets import asset_view
from .components.map import map_view
from .components.people import people_view
from .components.timeline import timeline_view
from .components.world import world_view


def create_ui() -> None:
    @ui.page("/")
    def index_page() -> None:
        with ui.tabs() as tabs:
            overview_tab = ui.tab("Overview")
            map_tab = ui.tab("Map & Spatial")
            people_tab = ui.tab("People & Lore")
            timeline_tab = ui.tab("Timeline & Simulation")
            export_tab = ui.tab("Export & Checker")

        with ui.tab_panels(tabs, value=overview_tab):
            with ui.tab_panel(overview_tab):
                world_view()
            with ui.tab_panel(map_tab):
                map_view()
            with ui.tab_panel(people_tab):
                people_view()
            with ui.tab_panel(timeline_tab):
                timeline_view()
            with ui.tab_panel(export_tab):
                asset_view()


def main() -> None:
    create_ui()
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()
