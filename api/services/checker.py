from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence

from ..models import (
    Activity,
    GameplayFeature,
    Household,
    MonsterZone,
    Person,
    POI,
    Quest,
    StoryArc,
    Event,
    Item,
)
from ..storage import load_dataset

ESSENTIAL_FEATURES = {"Quest Board", "Crafting Station", "Dungeon Entrance", "Arena"}
VARIETY_STYLES = {"combat", "social", "puzzle"}


WorldState = Dict[str, Sequence[object]]


def _load_world_state() -> WorldState:
    return {
        "persons": [Person.model_validate(item) for item in load_dataset("persons", factory=list)],
        "households": [Household.model_validate(item) for item in load_dataset("households", factory=list)],
        "events": [Event.model_validate(item) for item in load_dataset("events", factory=list)],
        "quests": [Quest.model_validate(item) for item in load_dataset("quests", factory=list)],
        "story_arcs": [StoryArc.model_validate(item) for item in load_dataset("story_arcs", factory=list)],
        "monster_zones": [MonsterZone.model_validate(item) for item in load_dataset("monster_zones", factory=list)],
        "features": [GameplayFeature.model_validate(item) for item in load_dataset("features", factory=list)],
        "items": [Item.model_validate(item) for item in load_dataset("items", factory=list)],
        "activities": [Activity.model_validate(item) for item in load_dataset("activities", factory=list)],
        "pois": [POI.model_validate(item) for item in load_dataset("pois", factory=list)],
    }


def _poi_lookup(pois: Sequence[POI]) -> Dict[str, str]:
    return {poi.id: poi.properties.name for poi in pois}


def validate_world(state: Optional[WorldState] = None, min_event_age: int = 10) -> List[str]:
    """Run AAA rulebook validation and return textual issues."""

    state = state or _load_world_state()
    persons = {person.person_id: person for person in state["persons"]}
    households = state["households"]
    events = state["events"]
    quests = state["quests"]
    arcs = state["story_arcs"]
    zones = state["monster_zones"]
    features = state["features"]
    items = state["items"]
    activities = state["activities"]
    pois = state["pois"]
    poi_name = _poi_lookup(pois)
    hub_ids = [poi.id for poi in pois if "hub" in poi.properties.layers]

    issues: List[str] = []

    # Household integrity
    for household in households:
        if household.location.poi_id is None:
            issues.append(f"Household {household.household_id} thiếu liên kết hub")
        seen = set()
        for member in household.members:
            if member.person_id in seen:
                issues.append(f"Trùng nhân vật {member.person_id} trong hộ {household.household_id}")
            seen.add(member.person_id)

    # Event eligibility
    for event in events:
        for person_id in event.linked_person_ids:
            person = persons.get(person_id)
            if not person:
                issues.append(f"Sự kiện {event.title} tham chiếu NPC không tồn tại {person_id}")
                continue
            age = event.date.year - person.birth_year
            if age < min_event_age:
                issues.append(f"{person.name} quá trẻ ({age}) cho sự kiện {event.title} năm {event.date.year}")

    # Story coverage per hub
    coverage_by_hub: Dict[str, List[str]] = defaultdict(list)
    for arc in arcs:
        for hub_id in arc.coverage_hubs:
            coverage_by_hub[hub_id].append(arc.name)
    for hub_id in hub_ids:
        if hub_id not in coverage_by_hub:
            issues.append(f"Hub {poi_name.get(hub_id, hub_id)} chưa có story arc chạm tới")

    # Monster zones coverage and variety
    style_counter = Counter()
    hubs_with_zones = set()
    for zone in zones:
        if zone.anchor_poi_id:
            hubs_with_zones.add(zone.anchor_poi_id)
        for encounter in zone.encounters:
            style_counter[encounter.style] += 1
    for hub_id in hub_ids:
        if hub_id not in hubs_with_zones:
            issues.append(f"Hub {poi_name.get(hub_id, hub_id)} thiếu monster zone gắn kết")
    for style in VARIETY_STYLES:
        if style_counter[style] == 0:
            issues.append(f"Encounter style {style} chưa được triển khai")

    # Feature coverage
    features_by_hub: Dict[str, set[str]] = defaultdict(set)
    for feature in features:
        features_by_hub[feature.poi_id].add(feature.feature_type)
    for hub_id in hub_ids:
        missing = sorted(ESSENTIAL_FEATURES - features_by_hub.get(hub_id, set()))
        if missing:
            hub_label = poi_name.get(hub_id, hub_id)
            issues.append(f"Hub {hub_label} thiếu tính năng: {', '.join(missing)}")

    # Item loot sources
    for item in items:
        if not item.sources:
            issues.append(f"Item {item.name} không có nguồn rơi")
        elif len(item.sources) == 1 and item.sources[0].drop_rate > 0.8:
            issues.append(f"Item {item.name} phụ thuộc một nguồn duy nhất")

    # Activity coverage
    activities_by_hub: Dict[str, List[Activity]] = defaultdict(list)
    for activity in activities:
        activities_by_hub[activity.poi_id].append(activity)
    for hub_id in hub_ids:
        if len(activities_by_hub.get(hub_id, [])) == 0:
            issues.append(f"Hub {poi_name.get(hub_id, hub_id)} chưa có hoạt động phụ")

    # Quest structure variety
    for quest in quests:
        if len(quest.nodes) < 4:
            issues.append(f"Quest {quest.title} quá ngắn (<4 nodes)")
        fetch_chain = sum(1 for node in quest.nodes.values() if "Thu thập" in node.text)
        if fetch_chain >= 3:
            issues.append(f"Quest {quest.title} có chuỗi fetch quá dài")

    return issues


def validation_summary() -> Dict[str, object]:
    state = _load_world_state()
    issues = validate_world(state)

    pois: Sequence[POI] = state["pois"]  # type: ignore[assignment]
    hub_ids = [poi.id for poi in pois if "hub" in poi.properties.layers]
    hub_total = max(1, len(hub_ids))

    arcs: Sequence[StoryArc] = state["story_arcs"]  # type: ignore[assignment]
    coverage_hubs = {hub for arc in arcs for hub in arc.coverage_hubs}
    story_coverage = round(len(coverage_hubs.intersection(hub_ids)) / hub_total * 100, 2)

    features: Sequence[GameplayFeature] = state["features"]  # type: ignore[assignment]
    features_by_hub: Dict[str, set[str]] = defaultdict(set)
    for feature in features:
        features_by_hub[feature.poi_id].add(feature.feature_type)
    feature_ready = sum(1 for hub in hub_ids if ESSENTIAL_FEATURES.issubset(features_by_hub.get(hub, set())))
    feature_coverage = round(feature_ready / hub_total * 100, 2)

    activities: Sequence[Activity] = state["activities"]  # type: ignore[assignment]
    activity_ready = sum(1 for hub in hub_ids if any(activity.poi_id == hub for activity in activities))
    activity_coverage = round(activity_ready / hub_total * 100, 2)

    zones: Sequence[MonsterZone] = state["monster_zones"]  # type: ignore[assignment]
    style_counter = Counter()
    for zone in zones:
        for encounter in zone.encounters:
            style_counter[encounter.style] += 1
    variety_score = round(min(1.0, sum(1 for style in VARIETY_STYLES if style_counter[style]) / len(VARIETY_STYLES)) * 100, 2)
    encounter_breakdown = {
        style: round(style_counter[style] / max(1, sum(style_counter.values())) * 100, 2)
        for style in VARIETY_STYLES
    }

    items: Sequence[Item] = state["items"]  # type: ignore[assignment]
    loot_healthy = sum(1 for item in items if item.sources)
    loot_health = round(loot_healthy / max(1, len(items)) * 100, 2)
    loot_distribution_counter = Counter()
    for item in items:
        for source in item.sources:
            loot_distribution_counter[source.source_type] += 1
    loot_distribution = {
        source: round(count / max(1, sum(loot_distribution_counter.values())) * 100, 2)
        for source, count in loot_distribution_counter.items()
    }

    export_ready = 100.0 if not issues else max(0.0, 100.0 - len(issues) * 5)

    schedule_overview: Dict[str, List[str]] = defaultdict(list)
    for activity in activities:
        schedule_overview[activity.schedule.cadence].append(activity.name)

    return {
        "issues": len(issues),
        "issue_messages": issues,
        "story_coverage": story_coverage,
        "feature_coverage": feature_coverage,
        "activity_coverage": activity_coverage,
        "monster_variety": variety_score,
        "encounter_breakdown": encounter_breakdown,
        "loot_health": loot_health,
        "loot_distribution": loot_distribution,
        "export_ready": export_ready,
        "schedule_overview": schedule_overview,
    }

