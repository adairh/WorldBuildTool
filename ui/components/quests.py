from nicegui import ui

from api.schemas import WorldRequest
from api.services import generate_world


def quest_view() -> None:
    """Show branching quest nodes and rewards."""

    bundle = generate_world(WorldRequest(seed=96, household_count=4, quest_count=3, event_count=6))
    with ui.column().classes("gap-3"):
        ui.label("Quest Studio").classes("text-2xl font-semibold")
        for quest in bundle.quests:
            with ui.card():
                ui.label(f"{quest.title}").classes("text-lg font-semibold")
                ui.label(quest.synopsis)
                ui.label("Rewards: " + ", ".join(quest.rewards))
                for node in quest.nodes.values():
                    with ui.expansion(f"Node {node.id}"):
                        if node.speaker:
                            ui.label(f"Speaker: {node.speaker}")
                        ui.label(node.dialogue)
                        for choice in node.choices:
                            ui.label(
                                f"→ {choice.text} [next: {choice.nextNodeId or 'end'}]"
                            )
