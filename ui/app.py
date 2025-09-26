from __future__ import annotations

from nicegui import ui

from .components.assets import qa_view
from .components.economy import economy_view
from .components.encounters import encounters_view
from .components.gameplay import gameplay_view
from .components.loot import loot_view
from .components.map import map_view
from .components.people import people_view
from .components.story import story_view
from .components.timeline import timeline_view
from .components.world import world_view


def create_ui() -> None:
    @ui.page("/")
    def index_page() -> None:
        with ui.tabs() as tabs:
            overview_tab = ui.tab("Command Desk")
            story_tab = ui.tab("Story & Quest")
            map_tab = ui.tab("Map & Encounters")
            people_tab = ui.tab("People & Timeline")
            systems_tab = ui.tab("Gameplay Systems")
            loot_tab = ui.tab("Loot & Economy")
            qa_tab = ui.tab("QA & Export")

        with ui.tab_panels(tabs, value=overview_tab):
            with ui.tab_panel(overview_tab):
                world_view()
            with ui.tab_panel(story_tab):
                story_view()
            with ui.tab_panel(map_tab):
                map_view()
                ui.separator().classes("my-4")
                encounters_view()
            with ui.tab_panel(people_tab):
                people_view()
                ui.separator().classes("my-4")
                timeline_view()
            with ui.tab_panel(systems_tab):
                gameplay_view()
            with ui.tab_panel(loot_tab):
                loot_view()
                ui.separator().classes("my-4")
                economy_view()
            with ui.tab_panel(qa_tab):
                qa_view()


def main() -> None:
    create_ui()
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()
