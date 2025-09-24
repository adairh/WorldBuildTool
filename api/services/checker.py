"""Consistency validators for TL-Forge world bundles."""

from __future__ import annotations

from typing import Dict, List, Optional

from ..schemas import Event, Person, Quest, WorldBundle


def check_age(person: Dict[str, int], event_year: int, min_age: int = 10) -> Optional[str]:
    """Return an error string when a person is younger than the allowed threshold."""

    birth_year = person.get("birthYear")
    if birth_year is None:
        return None
    if event_year - birth_year < min_age:
        return f"Error: {person.get('name', 'Unknown')} quá trẻ cho sự kiện {event_year}"
    return None


def _validate_event_participants(person_index: Dict[str, Person], event: Event) -> List[str]:
    errors: List[str] = []
    for participant_id in event.participantIds:
        if participant_id not in person_index:
            errors.append(
                f"Event {event.id} references missing participant {participant_id}."
            )
            continue
        person = person_index[participant_id]
        violation = check_age({"name": person.name, "birthYear": person.birthYear}, event.year, 12)
        if violation:
            errors.append(f"{violation} (event {event.id})")
    return errors


def _validate_quest_graph(quest: Quest) -> List[str]:
    errors: List[str] = []
    if quest.startingNodeId not in quest.nodes:
        errors.append(f"Quest {quest.id} missing starting node {quest.startingNodeId}")
    for node_id, node in quest.nodes.items():
        for choice in node.choices:
            if choice.nextNodeId and choice.nextNodeId not in quest.nodes:
                errors.append(
                    f"Quest {quest.id} choice {choice.id} points to missing node {choice.nextNodeId}"
                )
    return errors


def validate_world(bundle: WorldBundle) -> List[str]:
    """Run a suite of consistency checks against a world bundle."""

    errors: List[str] = []
    person_index = {person.id: person for person in bundle.persons}

    for event in bundle.events:
        errors.extend(_validate_event_participants(person_index, event))

    for quest in bundle.quests:
        errors.extend(_validate_quest_graph(quest))

    return errors


__all__ = ["check_age", "validate_world"]
