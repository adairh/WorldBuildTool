import pytest

pytest.importorskip("pydantic")

from api.schemas import WorldRequest
from api.services import check_age, generate_world, validate_world


def test_check_age_violation():
    person = {"name": "Nguyễn", "birthYear": 1290}
    result = check_age(person, event_year=1305, min_age=10)
    assert result is None

    result = check_age(person, event_year=1295, min_age=10)
    assert result == "Error: Nguyễn quá trẻ cho sự kiện 1295"


def test_world_validation_detects_missing_participant():
    request = WorldRequest(seed=77, household_count=2, quest_count=2, event_count=3)
    bundle = generate_world(request)
    bundle.events[0].participantIds.append("MISSING")
    errors = validate_world(bundle)
    assert any("missing participant" in err for err in errors)
