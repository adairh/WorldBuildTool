from datetime import date

from api.models import Event, Household, HouseholdLocation, Person
from api.services import validate_world
from api.storage import save_dataset


def test_validate_world_flags_missing_poi_and_young_member():
    child = Person(person_id="P-0001", name="Lý Văn", birth_year=1290, sex="M", household_id="HH-0001")
    household = Household(
        household_id="HH-0001",
        members=[child],
        location=HouseholdLocation(poi_id=None),
    )
    event = Event(
        event_id="EV-0001",
        date=date(1295, 1, 1),
        title="Lễ hội",
        linked_person_ids=[child.person_id],
    )

    save_dataset("households", [household.model_dump()])
    save_dataset("persons", [child.model_dump()])
    save_dataset("events", [event.model_dump()])

    issues = validate_world()
    assert any("missing POI" in issue for issue in issues)
    assert any("quá trẻ" in issue for issue in issues)
