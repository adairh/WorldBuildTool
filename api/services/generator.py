from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Dict, Iterable, List, Sequence, Tuple
from uuid import uuid4

from faker import Faker

from ..models import (
    Activity,
    ActivitySchedule,
    EncounterProfile,
    GameplayFeature,
    Household,
    HouseholdLedger,
    HouseholdLocation,
    Item,
    LootSource,
    MonsterZone,
    Person,
    POI,
    Geometry,
    POIProperties,
    Quest,
    DialogueNode,
    StoryArc,
    StoryBeat,
)
from .checker import ESSENTIAL_FEATURES
from ..storage import load_dataset, save_dataset

fake = Faker("vi_VN")

# --- Templates -----------------------------------------------------------------

HUB_TEMPLATES: Sequence[Dict[str, object]] = (
    {
        "name": "Hoàng thành Thăng Long",
        "description": "Trung tâm triều đình, nơi hội tụ main arc và boss quốc gia.",
        "layers": ["hub", "story", "military"],
        "tags": ["royal", "boss", "approval"],
        "kind": "district",
    },
    {
        "name": "Phố Thương Nhân Đồng Xuân",
        "description": "Chợ chính, tuyến kinh tế và các arc thương hội.",
        "layers": ["hub", "economy", "craft"],
        "tags": ["vendor", "quest"],
        "kind": "market",
    },
    {
        "name": "Khu Đền Quán Trấn Vũ",
        "description": "Trung tâm tôn giáo và arc tâm linh của dân thành.",
        "layers": ["hub", "religion", "story"],
        "tags": ["ritual", "festival"],
        "kind": "temple",
    },
    {
        "name": "Bến Sông Nhị Hà",
        "description": "Cửa ngõ thương mại đường thủy, hoạt động vận chuyển.",
        "layers": ["hub", "transport", "economy"],
        "tags": ["trade", "fleet"],
        "kind": "harbor",
    },
    {
        "name": "Phường Thợ Gốm Bát Tràng",
        "description": "Làng nghề thủ công, quest nghề nghiệp và crafting.",
        "layers": ["hub", "craft", "story"],
        "tags": ["crafting", "daily"],
        "kind": "craft",
    },
    {
        "name": "Giáp Văn Nhân",
        "description": "Khu học giả, quest nghiên cứu và arc phái văn hiến.",
        "layers": ["hub", "scholar", "story"],
        "tags": ["lore", "timeline"],
        "kind": "district",
    },
)

FEATURE_LIBRARY: Sequence[Tuple[str, str]] = (
    ("Arena of the White Tiger", "Arena"),
    ("Grand Quest Board", "Quest Board"),
    ("Song Long Fishing Wharf", "Fishing"),
    ("Royal Craft Hall", "Crafting Station"),
    ("Imperial Dungeon Gate", "Dungeon Entrance"),
    ("Lotus PvP Grounds", "PvP Zone"),
    ("Festival Plaza", "Festival"),
)

MONSTER_POOLS: Sequence[Tuple[str, List[str]]] = (
    ("Bandit Raiders", ["Bandit", "Cutthroat", "Scout"]),
    ("River Spirits", ["Thuồng Luồng", "Thủy Quái", "Nàng Tiên Nước"]),
    ("Temple Phantoms", ["Hồn Ma", "Yêu Ảnh", "Thiên Linh Cái"]),
    ("Craft Guild Saboteurs", ["Nội Gián", "Độc Sư", "Trộm Nghề"]),
)

ITEM_BLUEPRINTS: Sequence[Tuple[str, str, str, str]] = (
    ("Trấn Quốc Kiếm", "weapon", "legendary", "Kiếm trấn giữ hoàng thành."),
    ("Hải Thần Trượng", "weapon", "epic", "Pháp trượng điều khiển thủy khí."),
    ("Phù Chuẩn Thương Hội", "accessory", "rare", "Bùa hộ mệnh thương nhân Đồng Xuân."),
    ("Giáp Gốm Cửu Long", "armor", "rare", "Giáp gốm nung cho hiệp sĩ phường thợ."),
    ("Pháp Bảo Trấn Vũ", "trinket", "epic", "Ấn chú linh khí từ đền Trấn Vũ."),
)

ACTIVITY_LIBRARY: Sequence[Tuple[str, str, str]] = (
    ("Đua Thuyền Nhị Hà", "weekly", "competition"),
    ("Đấu Cờ Vua Văn Nhân", "daily", "mind"),
    ("Lễ Rước Thần", "seasonal", "festival"),
    ("Chợ Đêm Đồng Xuân", "nightly", "market"),
    ("Hội Thợ Lửa", "weekly", "craft"),
)

QUEST_THEMES: Sequence[str] = (
    "Âm mưu trong hoàng thành",
    "Giải cứu đoàn thương hội",
    "Giao ước với thủy thần",
    "Giữ bí quyết nghề gốm",
    "Thư họa và kiếm pháp",)


# --- Helpers -------------------------------------------------------------------

def _seed_everything(seed: int | None) -> None:
    if seed is not None:
        random.seed(seed)
        fake.seed_instance(seed)


def _random_coordinates() -> List[float]:
    base_lon = 105.84
    base_lat = 21.03
    return [base_lon + random.uniform(-0.05, 0.05), base_lat + random.uniform(-0.05, 0.05)]


def _polygon_around(center: List[float], spread: float = 0.01) -> List[List[float]]:
    lon, lat = center
    return [
        [lon - spread, lat - spread],
        [lon + spread, lat - spread],
        [lon + spread, lat + spread],
        [lon - spread, lat + spread],
    ]


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
    coords = coordinates or _random_coordinates()
    geometry = Geometry(coordinates=coords)
    properties = POIProperties(
        name=name,
        kind=kind,
        layers=list(layers or []),
        tags=list(tags or []),
        description=description,
    )
    poi = POI(id=poi_id, geometry=geometry, properties=properties)
    existing = list(load_dataset("pois", factory=list))
    existing.append(poi.model_dump())
    save_dataset("pois", existing)
    return poi


def _ensure_base_pois(seed: int | None = None) -> List[POI]:
    pois = [POI.model_validate(item) for item in load_dataset("pois", factory=list)]
    if pois:
        return pois
    _seed_everything(seed or 42)
    generated: List[POI] = []
    for template in HUB_TEMPLATES:
        coords = _random_coordinates()
        generated.append(
            generate_poi(
                template["name"],
                layers=template["layers"],
                tags=template["tags"],
                coordinates=coords,
                description=template["description"],
                kind=str(template["kind"]),
            )
        )
    return generated


def _person_id(idx: int) -> str:
    return f"P-{idx:04d}"


def _household_id(idx: int) -> str:
    return f"HH-{idx:04d}"


def _quest_id(idx: int) -> str:
    return f"Q-{idx:03d}"


def _story_arc_id(idx: int) -> str:
    return f"ARC-{idx:02d}"


def _monster_zone_id(idx: int) -> str:
    return f"ZONE-{idx:02d}"


def _feature_id(idx: int) -> str:
    return f"FEAT-{idx:02d}"


def _item_id(idx: int) -> str:
    return f"ITEM-{idx:03d}"


def _activity_id(idx: int) -> str:
    return f"ACT-{idx:03d}"


# --- Generation routines -------------------------------------------------------

def generate_households(count: int, seed: int | None = None, poi_pool: List[str] | None = None) -> List[Household]:
    _seed_everything(seed)
    pois = poi_pool or [poi.id for poi in _ensure_base_pois(seed)]
    households: List[Household] = []
    persons: List[Person] = []

    districts = [
        "Hoàng thành",
        "Đồng Xuân",
        "Trấn Vũ",
        "Nhị Hà",
        "Bát Tràng",
        "Văn Nhân",
    ]
    allegiances = ["Triều đình", "Thương hội", "Tế đàn", "Thủy quân", "Nghề thủ công", "Văn phái"]
    specialties = ["quan lại", "thương nhân", "thầy cúng", "thủy thủ", "thợ gốm", "học giả"]

    for idx in range(count):
        household_id = _household_id(idx + 1)
        location = HouseholdLocation(poi_id=random.choice(pois) if pois else None)
        member_count = random.randint(3, 5)
        members: List[Person] = []
        for member_idx in range(member_count):
            sex = random.choice(["M", "F"])
            birth_year = random.randint(1240, 1275)
            profession = random.choice(
                ["quan lại", "thương nhân", "thợ gốm", "thầy đồ", "binh sĩ", "ngư dân", "ngự y"]
            )
            person = Person(
                person_id=_person_id(len(persons) + 1),
                name=fake.name_male() if sex == "M" else fake.name_female(),
                birth_year=birth_year,
                sex=sex,
                profession=profession,
                household_id=household_id,
                home_poi_id=location.poi_id,
                relation="gia chủ" if member_idx == 0 else "thành viên",
            )
            members.append(person)
            persons.append(person)

        ledger = HouseholdLedger(
            silver=random.randint(50, 500),
            rice=random.randint(100, 600),
            influence=random.randint(0, 100),
            artisans=random.randint(1, 10),
        )
        household = Household(
            household_id=household_id,
            house_type=random.choice(["nhà 3 gian", "nhà ống", "nhà mái ngói", "nhà sàn"]),
            status="occupied",
            district=random.choice(districts),
            allegiance=random.choice(allegiances),
            specialty=random.choice(specialties),
            location=location,
            members=members,
            notes=f"Seed {seed}" if seed is not None else None,
            ledger=ledger,
        )
        households.append(household)

    save_dataset("households", [household.model_dump() for household in households])
    save_dataset("persons", [person.model_dump() for person in persons])
    return households


def generate_timeline(days: int = 10, seed: int | None = None) -> List[Dict[str, object]]:
    _seed_everything(seed)
    events: List[Dict[str, object]] = []
    base_date = date(1285, 1, 1)
    people = load_dataset("persons", factory=list)
    person_ids = [item["person_id"] for item in people]
    poi_ids = [item["id"] for item in load_dataset("pois", factory=list)]

    event_types = ["festival", "raid", "council", "trade", "training"]
    for idx in range(days):
        event_date = base_date + timedelta(days=idx * max(1, random.randint(1, 5)))
        linked_people = random.sample(person_ids, k=min(len(person_ids), random.randint(1, 3))) if person_ids else []
        linked_pois = random.sample(poi_ids, k=min(len(poi_ids), random.randint(1, 2))) if poi_ids else []
        events.append(
            {
                "event_id": f"EV-{idx+1:04d}",
                "date": event_date.isoformat(),
                "title": f"Sự kiện {idx+1}",
                "description": f"Diễn biến {event_types[idx % len(event_types)]} tại Thăng Long.",
                "linked_person_ids": linked_people,
                "linked_poi_ids": linked_pois,
                "type": event_types[idx % len(event_types)],
                "tags": ["seasonal" if idx % 4 == 0 else "daily"],
            }
        )

    save_dataset("events", events)
    return events


def _build_quest_nodes(quest_id: str, theme: str) -> Dict[str, DialogueNode]:
    nodes: Dict[str, DialogueNode] = {}
    beats = [
        ("gather", "Thu thập manh mối"),
        ("social", "Thương lượng"),
        ("combat", "Đột kích"),
        ("puzzle", "Giải mật đạo"),
        ("climax", "Đối đầu cuối"),
    ]
    previous_node = None
    for idx, (tag, label) in enumerate(beats, start=1):
        node_id = f"{quest_id}-N{idx}"
        choices = [f"Chọn {tag}", f"Biến thể {tag}"]
        if idx == len(beats):
            choices.append("Kết thúc")
        nodes[node_id] = DialogueNode(
            node_id=node_id,
            speaker="Narrator" if idx == 1 else "NPC",
            text=f"[{label}] {theme}",
            choices=choices,
        )
        if previous_node:
            nodes[previous_node].choices = [f"Tiến tới {node_id}"]
        previous_node = node_id
    return nodes


def generate_quests(count: int, seed: int | None = None) -> List[Quest]:
    _seed_everything(seed)
    quests: List[Quest] = []
    for idx in range(count):
        quest_id = _quest_id(idx + 1)
        theme = QUEST_THEMES[idx % len(QUEST_THEMES)]
        nodes = _build_quest_nodes(quest_id, theme)
        quest = Quest(
            quest_id=quest_id,
            title=theme,
            description=f"Questline {theme} gồm nhiều thể loại gameplay.",
            nodes=nodes,
            start_node=list(nodes.keys())[0],
            tags=["combat", "social", "puzzle"],
        )
        quests.append(quest)
    save_dataset("quests", [quest.model_dump() for quest in quests])
    return quests


def generate_story_arcs(quests: List[Quest], seed: int | None = None) -> List[StoryArc]:
    _seed_everything(seed)
    hubs = [poi["id"] for poi in load_dataset("pois", factory=list)]
    arc_types = ["Main", "Faction", "Class", "Seasonal"]
    arcs: List[StoryArc] = []
    for idx, arc_type in enumerate(arc_types, start=1):
        quest_slice = quests[(idx - 1) : (idx + 1)] or quests
        coverage = random.sample(hubs, k=min(len(hubs), max(2, len(hubs) - 1))) if hubs else []
        beats = []
        for beat_idx, quest in enumerate(quest_slice, start=1):
            beat_id = f"{_story_arc_id(idx)}-B{beat_idx}"
            beats.append(
                StoryBeat(
                    beat_id=beat_id,
                    quest_id=quest.quest_id,
                    stage=["Setup", "Escalation", "Climax"][beat_idx % 3],
                    description=f"{quest.title} mở rộng arc {arc_type}.",
                    poi_id=random.choice(coverage) if coverage else "",
                    timeline_ref=f"EV-{beat_idx:04d}",
                    tone=random.choice(["heroic", "mysterious", "political"]),
                    requires_cinematic=beat_idx % 2 == 0,
                )
            )
        arc = StoryArc(
            arc_id=_story_arc_id(idx),
            name=f"{arc_type} Arc",
            arc_type=arc_type,
            focus=random.choice([
                "Defense of the Citadel",
                "Merchant intrigue",
                "Spiritual trials",
                "Artisan pride",
                "Scholarly duel",
            ]),
            coverage_hubs=coverage,
            questline_ids=[quest.quest_id for quest in quest_slice],
            beats=beats,
            cinematic_hooks=[beat.beat_id for beat in beats if beat.requires_cinematic],
            approvals=["LGD pending"],
        )
        arcs.append(arc)
    save_dataset("story_arcs", [arc.model_dump() for arc in arcs])
    return arcs


def generate_monster_zones(seed: int | None = None) -> List[MonsterZone]:
    _seed_everything(seed)
    pois = [POI.model_validate(item) for item in load_dataset("pois", factory=list)]
    zones: List[MonsterZone] = []
    for idx, poi in enumerate(pois or [], start=1):
        pool_name, monsters = MONSTER_POOLS[(idx - 1) % len(MONSTER_POOLS)]
        center = poi.geometry.coordinates if pois else _random_coordinates()
        polygon = _polygon_around(center, spread=0.02)
        encounters = [
            EncounterProfile(
                encounter_id=f"{_monster_zone_id(idx)}-E{enc_idx}",
                style=style,
                monster_types=random.sample(monsters, k=min(len(monsters), 2)),
                spawn_weight=random.uniform(0.1, 0.5),
                recommended_power=random.choice(["Party", "Solo", "Raid"]),
                loot_table_ids=[],
                notes=f"{style.title()} encounter in {pool_name}",
            )
            for enc_idx, style in enumerate(["combat", "social", "puzzle"], start=1)
        ]
        zone = MonsterZone(
            zone_id=_monster_zone_id(idx),
            name=f"{pool_name} Territory",
            faction=random.choice(["Outlaws", "River Court", "Temple Wardens", "Guild Shadows"]),
            anchor_poi_id=poi.id if pois else "",
            level_range=[10 * idx, 10 * idx + 5],
            polygon=polygon,
            spawn_windows=["day", "night" if idx % 2 == 0 else "dawn"],
            encounters=encounters,
        )
        zones.append(zone)
    if not zones:
        pool_name, monsters = MONSTER_POOLS[0]
        encounters = [
            EncounterProfile(
                encounter_id=f"{_monster_zone_id(1)}-E{enc_idx}",
                style=style,
                monster_types=random.sample(monsters, k=min(len(monsters), 2)),
                spawn_weight=random.uniform(0.1, 0.5),
                recommended_power="Party",
                loot_table_ids=[],
                notes=f"Fallback {style}",
            )
            for enc_idx, style in enumerate(["combat", "social", "puzzle"], start=1)
        ]
        zones.append(
            MonsterZone(
                zone_id=_monster_zone_id(1),
                name=f"{pool_name} Territory",
                faction="Outlaws",
                anchor_poi_id="",
                level_range=[10, 15],
                polygon=_polygon_around(_random_coordinates(), spread=0.02),
                spawn_windows=["day"],
                encounters=encounters,
            )
        )
    save_dataset("monster_zones", [zone.model_dump() for zone in zones])
    return zones


def generate_gameplay_features(seed: int | None = None) -> List[GameplayFeature]:
    _seed_everything(seed)
    pois = [item["id"] for item in load_dataset("pois", factory=list)]
    features: List[GameplayFeature] = []
    essential_features = {feature_type for _, feature_type in FEATURE_LIBRARY if feature_type in ESSENTIAL_FEATURES}
    optional_features = [(name, feature_type) for name, feature_type in FEATURE_LIBRARY if feature_type not in ESSENTIAL_FEATURES]

    idx = 0
    for poi_idx, poi_id in enumerate(pois or ["HUB-000"]):
        for feature_type in sorted(essential_features):
            idx += 1
            feature = GameplayFeature(
                feature_id=_feature_id(idx),
                feature_type=feature_type,
                poi_id=poi_id,
                unlock_condition=random.choice([
                    "Main arc chapter 2",
                    "Faction rep Friendly",
                    "Complete dungeon intro",
                ]),
                required_level=random.choice(["10", "20", "30"]),
                supports_groups=feature_type not in {"Quest Board"},
                notes=f"{feature_type} Hub {poi_idx + 1}",
            )
            features.append(feature)

    for name, feature_type in optional_features:
        idx += 1
        feature = GameplayFeature(
            feature_id=_feature_id(idx),
            feature_type=feature_type,
            poi_id=random.choice(pois) if pois else "",
            unlock_condition=random.choice([
                "Seasonal event",
                "Faction rank Honored",
                "Quest board weekly",
            ]),
            required_level=random.choice(["15", "25", "35"]),
            supports_groups=True,
            notes=name,
        )
        features.append(feature)
    save_dataset("features", [feature.model_dump() for feature in features])
    return features


def generate_activities(seed: int | None = None) -> List[Activity]:
    _seed_everything(seed)
    pois = [item["id"] for item in load_dataset("pois", factory=list)]
    activities: List[Activity] = []
    for idx, poi_id in enumerate(pois or ["HUB-000"], start=1):
        name, cadence, category = ACTIVITY_LIBRARY[(idx - 1) % len(ACTIVITY_LIBRARY)]
        activity = Activity(
            activity_id=_activity_id(idx),
            name=f"{name} {idx}",
            activity_type=category,
            poi_id=poi_id,
            summary=f"Hoạt động {category} với lịch {cadence}.",
            rewards=[random.choice(["reputation", "loot", "currency"])],
            schedule=ActivitySchedule(
                cadence=cadence,
                days=["Mon", "Thu"] if cadence == "weekly" else ["Daily"],
                seasons=["Xuân", "Hạ"] if cadence == "seasonal" else ["Quanh năm"],
            ),
            approvals=["Content Lead"] if idx % 2 == 0 else [],
        )
        activities.append(activity)
    # add a couple of floating seasonal activities for flavor
    for extra_idx, (name, cadence, category) in enumerate(ACTIVITY_LIBRARY[:2], start=len(activities) + 1):
        activities.append(
            Activity(
                activity_id=_activity_id(extra_idx),
                name=f"{name} Special",
                activity_type=category,
                poi_id=random.choice(pois) if pois else "",
                summary=f"{category} đặc biệt", 
                rewards=["legendary loot" if category == "competition" else "reputation"],
                schedule=ActivitySchedule(
                    cadence=cadence,
                    days=["Festival"],
                    seasons=["Tết", "Trung Thu"] if cadence == "seasonal" else ["Quanh năm"],
                ),
                approvals=["LGD"],
            )
        )
    save_dataset("activities", [activity.model_dump() for activity in activities])
    return activities


def generate_items(
    quests: List[Quest], zones: List[MonsterZone], features: List[GameplayFeature], seed: int | None = None
) -> List[Item]:
    _seed_everything(seed)
    items: List[Item] = []
    quest_ids = [quest.quest_id for quest in quests]
    zone_ids = [zone.zone_id for zone in zones]
    feature_ids = [feature.feature_id for feature in features]

    for idx, (name, slot, rarity, description) in enumerate(ITEM_BLUEPRINTS, start=1):
        sources: List[LootSource] = []
        if quest_ids:
            sources.append(
                LootSource(
                    source_type="quest",
                    reference_id=random.choice(quest_ids),
                    drop_rate=round(random.uniform(0.2, 0.5), 2),
                    notes="Quest reward",
                )
            )
        if zone_ids:
            sources.append(
                LootSource(
                    source_type="monster",
                    reference_id=random.choice(zone_ids),
                    drop_rate=round(random.uniform(0.05, 0.15), 2),
                    notes="Rare drop",
                )
            )
        if feature_ids and idx % 2 == 0:
            sources.append(
                LootSource(
                    source_type="feature",
                    reference_id=random.choice(feature_ids),
                    drop_rate=round(random.uniform(0.1, 0.3), 2),
                    notes="Crafting output",
                )
            )

        item = Item(
            item_id=_item_id(idx),
            name=name,
            slot=slot,
            rarity=rarity,
            description=description,
            progression_stage=random.choice(["mid", "late", "endgame"]),
            sources=sources,
        )
        items.append(item)
    save_dataset("items", [item.model_dump() for item in items])
    return items


def regenerate_foundation(seed: int = 42) -> Dict[str, List[Dict[str, object]]]:
    """Reset the entire storage to a reproducible, feature-rich dataset."""

    save_dataset("pois", [])
    save_dataset("households", [])
    save_dataset("persons", [])
    save_dataset("events", [])
    save_dataset("quests", [])
    save_dataset("story_arcs", [])
    save_dataset("monster_zones", [])
    save_dataset("features", [])
    save_dataset("items", [])
    save_dataset("activities", [])

    pois = _ensure_base_pois(seed)
    households = generate_households(len(pois) * 2, seed=seed, poi_pool=[poi.id for poi in pois])
    events = generate_timeline(14, seed=seed)
    quests = generate_quests(6, seed=seed)
    arcs = generate_story_arcs(quests, seed=seed)
    zones = generate_monster_zones(seed=seed)
    features = generate_gameplay_features(seed=seed)
    activities = generate_activities(seed=seed)
    items = generate_items(quests, zones, features, seed=seed)

    return {
        "pois": [poi.model_dump() for poi in pois],
        "households": [household.model_dump() for household in households],
        "events": events,
        "quests": [quest.model_dump() for quest in quests],
        "story_arcs": [arc.model_dump() for arc in arcs],
        "monster_zones": [zone.model_dump() for zone in zones],
        "features": [feature.model_dump() for feature in features],
        "activities": [activity.model_dump() for activity in activities],
        "items": [item.model_dump() for item in items],
    }

