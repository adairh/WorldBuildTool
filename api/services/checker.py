from __future__ import annotations

from datetime import date
from typing import Dict, List

from ..models import Event, Household, Person
from ..storage import load_dataset


def _load_people() -> List[Person]:
    return [Person.model_validate(item) for item in load_dataset("persons", factory=list)]


def _load_households() -> List[Household]:
    return [Household.model_validate(item) for item in load_dataset("households", factory=list)]


def _load_events() -> List[Event]:
    return [Event.model_validate(item) for item in load_dataset("events", factory=list)]


def validate_world(min_event_age: int = 10) -> List[str]:
    """Run consistency checks across stored datasets."""

    issues: List[str] = []
    people = {person.person_id: person for person in _load_people()}
    households = _load_households()
    events = _load_events()

    for household in households:
        if household.location.poi_id is None:
            issues.append(f"Household {household.household_id} missing POI reference")
        seen = set()
        for member in household.members:
            if member.person_id in seen:
                issues.append(f"Duplicate member id {member.person_id} in household {household.household_id}")
            seen.add(member.person_id)

    for event in events:
        for person_id in event.linked_person_ids:
            person = people.get(person_id)
            if not person:
                issues.append(f"Event {event.event_id} references unknown person {person_id}")
                continue
            age = person.age_in_year(event.date.year)
            if age is not None and age < min_event_age:
                issues.append(
                    f"{person.name} quá trẻ ({age}) cho sự kiện {event.title} năm {event.date.year}"
                )

    return issues


def validation_summary() -> Dict[str, int]:
    issues = validate_world()
    return {"issues": len(issues)}
