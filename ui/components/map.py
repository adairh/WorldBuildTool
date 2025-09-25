import json

from nicegui import ui

from api.schemas import WorldRequest
from api.services import generate_world

try:  # pragma: no cover - optional dependency
    import leafmap
except Exception:  # pragma: no cover
    leafmap = None


def map_view() -> None:
    """Render a spatial digest of generated POIs."""

    bundle = generate_world(WorldRequest(seed=52, household_count=3, quest_count=1, event_count=4))
    with ui.column().classes("w-full gap-2"):
        ui.label("POI Atlas").classes("text-2xl font-semibold")
        if leafmap is None:
            ui.label("Leafmap unavailable; displaying textual atlas instead.")
        else:
            city_map = leafmap.Map(center=[21.0285, 105.8542], zoom=11)
            city_map.add_basemap("HYBRID")
            map_html = city_map.to_html()
            ui.element("iframe").style(
                "width: 100%; height: 24rem; border: 1px solid #ccc; border-radius: 0.5rem;"
            ).props(f"srcdoc={json.dumps(map_html)}")
        for poi in bundle.pois[:8]:
            with ui.card():
                ui.label(f"{poi.name} [{poi.category}]")
                ui.label(f"District: {poi.district}")
                ui.label(poi.description)
                ui.label("Tags: " + ", ".join(poi.tags))
