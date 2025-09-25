from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Dict, Iterable, List, cast
from uuid import uuid4

from faker import Faker

from ..models import Event, Geometry, Household, HouseholdLocation, Person, POI, POIProperties
from ..storage import load_dataset, save_dataset

fake = Faker("vi_VN")

HOUSE_TYPES = ["nhà 3 gian", "nhà ống", "nhà gianh", "nhà mái ngói"]
PROFESSIONS = [
    "thương nhân",
    "ngư dân",
    "thợ rèn",
    "thầy đồ",
    "binh sĩ",
    "thợ gốm",
    "dệt vải",
    "nông dân",
]


def _random_name(sex: str) -> str:
    return fake.name_male() if sex == "M" else fake.name_female()


def _person_id(idx: int) -> str:
    return f"P-{idx:04d}"


def _household_id(idx: int) -> str:
    return f"HH-{idx:04d}"


def generate_poi(
    name: str,
    layers: Iterable[str] | None = None,
    tags: Iterable[str] | None = None,
    *,
    coordinates: List[float] | None = None,
    description: str = "",
    kind: str = "landmark",
) -> POI:
    poi_id = f"POI-{uuid4().hex[:6].upper()}"
    coords = coordinates or [106.0 + random.random() / 10, 21.0 + random.random() / 10]
    geometry = Geometry(coordinates=coords)
    properties = POIProperties(
        name=name,
        kind=kind,
        layers=list(layers or []),
        tags=list(tags or []),
        description=description,
    )
    poi = POI(id=poi_id, geometry=geometry, properties=properties)
    existing = cast(List[Dict[str, object]], list(load_dataset("pois", factory=list)))
    existing.append(poi.model_dump())
    save_dataset("pois", existing)
    return poi


def generate_households(count: int, seed: int | None = None, poi_pool: List[str] | None = None) -> List[Household]:
    if seed is not None:
        random.seed(seed)
        fake.seed_instance(seed)

    poi_ids = poi_pool or [item["id"] for item in load_dataset("pois", factory=list)]
    households: List[Household] = []
    persons: List[Person] = []

    for idx in range(count):
        household_id = _household_id(idx + 1)
        house_type = random.choice(HOUSE_TYPES)
        location = HouseholdLocation(poi_id=random.choice(poi_ids) if poi_ids else None)
        member_count = random.randint(2, 5)
        members: List[Person] = []
        for member_idx in range(member_count):
            sex = random.choice(["M", "F"])
            birth_year = random.randint(1240, 1275)
            person = Person(
                person_id=_person_id(len(persons) + 1),
                name=_random_name(sex),
                birth_year=birth_year,
                sex=sex,
                profession=random.choice(PROFESSIONS),
                household_id=household_id,
                home_poi_id=location.poi_id,
                relation="gia chủ" if member_idx == 0 else "thành viên",
            )
            persons.append(person)
            members.append(person)

        household = Household(
            household_id=household_id,
            house_type=house_type,
            members=members,
            location=location,
            notes=f"Seed {seed}" if seed is not None else None,
        )
        households.append(household)

    household_payload = [household.model_dump() for household in households]
    person_payload = [person.model_dump() for person in persons]
    save_dataset("households", household_payload)
    save_dataset("persons", person_payload)
    return households


def generate_timeline(days: int = 10, seed: int | None = None) -> List[Event]:
    if seed is not None:
        random.seed(seed)

    events: List[Event] = []
    base_date = date(1285, 1, 1)
    people = load_dataset("persons", factory=list)
    person_ids = [item["person_id"] for item in people]
    poi_ids = [item["id"] for item in load_dataset("pois", factory=list)]

    for idx in range(days):
        event_date = base_date + timedelta(days=idx * max(1, random.randint(1, 6)))
        linked_people = random.sample(person_ids, k=min(len(person_ids), random.randint(0, 2))) if person_ids else []
        linked_pois = random.sample(poi_ids, k=min(len(poi_ids), random.randint(0, 2))) if poi_ids else []
        event = Event(
            event_id=f"EV-{idx+1:04d}",
            date=event_date,
            title=f"Sự kiện #{idx+1}",
            description=f"Nhật ký ngày {event_date.isoformat()} của Thăng Long.",
            linked_person_ids=linked_people,
            linked_poi_ids=linked_pois,
            tags=["festival" if idx % 3 == 0 else "daily"],
        )
        events.append(event)

    save_dataset("events", [event.model_dump() for event in events])
    return events


def regenerate_foundation(seed: int = 42) -> Dict[str, List[Dict[str, object]]]:
    """Reset the storage to a reproducible baseline."""

    save_dataset("pois", [])
    save_dataset("households", [])
    save_dataset("persons", [])
    save_dataset("events", [])

    random.seed(seed)
    fake.seed_instance(seed)

    pois = [
        generate_poi("Chợ Tế Xuyên", layers=["economy", "transport"], tags=["grain", "textile"]),
        generate_poi("Đình Đông Bộ Đầu", layers=["religion", "community"], tags=["festival"]),
        generate_poi("Bến sông Lô Giang", layers=["transport"], tags=["port"]),
    ]
    households = generate_households(5, seed=seed, poi_pool=[poi.id for poi in pois])
    events = generate_timeline(7, seed=seed)
    return {
        "pois": [poi.model_dump() for poi in pois],
        "households": [household.model_dump() for household in households],
        "events": [event.model_dump() for event in events],
    }
