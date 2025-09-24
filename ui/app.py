from nicegui import ui

from .components.assets import asset_view
from .components.economy import economy_view
from .components.map import map_view
from .components.people import people_view
from .components.quests import quest_view
from .components.timeline import timeline_view
from .components.world import world_view


def create_ui() -> None:
    @ui.page("/")
    def index_page():
        with ui.tabs() as tabs:
            world_tab = ui.tab("World Overview")
            map_tab = ui.tab("Map Studio")
            people_tab = ui.tab("People Studio")
            timeline_tab = ui.tab("Timeline Studio")
            quest_tab = ui.tab("Quest Studio")
            economy_tab = ui.tab("Economy Lite")
            asset_tab = ui.tab("Asset Studio")

        with ui.tab_panels(tabs, value=world_tab):
            with ui.tab_panel(world_tab):
                world_view()
            with ui.tab_panel(map_tab):
                map_view()
            with ui.tab_panel(people_tab):
                people_view()
            with ui.tab_panel(timeline_tab):
                timeline_view()
            with ui.tab_panel(quest_tab):
                quest_view()
            with ui.tab_panel(economy_tab):
                economy_view()
            with ui.tab_panel(asset_tab):
                asset_view()


def main() -> None:
    create_ui()
    ui.run()


if __name__ == "__main__":
    main()
