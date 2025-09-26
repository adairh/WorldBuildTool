from __future__ import annotations

from nicegui import ui

from .components.assets import asset_view
from .components.map import map_view
from .components.people import people_view
from .components.quests import quests_view
from .components.timeline import timeline_view
from .components.world import world_view


def create_ui() -> None:
    @ui.page("/")
    def index_page() -> None:
        with ui.tabs() as tabs:
            overview_tab = ui.tab("Command Desk")
            map_tab = ui.tab("Map Studio")
            people_tab = ui.tab("People Studio")
            timeline_tab = ui.tab("Timeline Studio")
            quests_tab = ui.tab("Quest Studio")
            assets_tab = ui.tab("Asset Library")

        with ui.tab_panels(tabs, value=overview_tab):
            with ui.tab_panel(overview_tab):
                world_view()
            with ui.tab_panel(map_tab):
                map_view()
            with ui.tab_panel(people_tab):
                people_view()
            with ui.tab_panel(timeline_tab):
                timeline_view()
            with ui.tab_panel(quests_tab):
                quests_view()
            with ui.tab_panel(assets_tab):
                asset_view()


def main() -> None:
    create_ui()
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()
