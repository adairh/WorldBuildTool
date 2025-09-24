from datetime import date

from nicegui import ui

from api.schemas import WorldRequest
from api.services import generate_world

try:  # pragma: no cover - optional dependency
    import plotly.express as px
except Exception:  # pragma: no cover
    px = None


def timeline_view() -> None:
    """Visualize generated events."""

    bundle = generate_world(WorldRequest(seed=88, household_count=5, quest_count=3, event_count=8))
    events = bundle.events

    if not events:
        ui.label("No events generated.")
        return

    if px is None:
        with ui.column().classes("gap-2"):
            ui.label("Timeline Studio").classes("text-2xl font-semibold")
            for event in events:
                ui.label(f"{event.year} {event.season}: {event.title} → {event.outcome}")
        return

    frame = {
        "start": [date(event.year, 1, 1) for event in events],
        "finish": [date(event.year, 1, 2) for event in events],
        "title": [event.title for event in events],
        "type": [event.type for event in events],
    }
    fig = px.timeline(frame, x_start="start", x_end="finish", y="title", color="type")
    fig.update_layout(title="Timeline Studio", showlegend=True, height=400)
    ui.plotly(fig)
