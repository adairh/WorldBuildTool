from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence

from ..models import (
    Activity,
    City,
    District,
    GameplayFeature,
    Household,
    MonsterZone,
    NPCMix,
    Person,
    POI,
    Quest,
    StoryArc,
    Event,
    Item,
    TradeNode,
    TradeRoute,
    Festival,
    FactionPresence,
    Hostility,
    AccessRule,
    LawCrimeParams,
    DistrictCrimeOverride,
    Tuning,
)
from ..storage import load_dataset

ESSENTIAL_FEATURES = {"Quest Board", "Crafting Station", "Dungeon Entrance", "Arena"}
VARIETY_STYLES = {"combat", "social", "puzzle"}


WorldState = Dict[str, object]


def _load_world_state() -> WorldState:
    city_data = load_dataset("city", factory=dict)
    law_data = load_dataset("law_params", factory=dict)
    tuning_data = load_dataset("tuning", factory=dict)
    return {
        "city": City.model_validate(city_data) if city_data else None,
        "districts": [District.model_validate(item) for item in load_dataset("districts", factory=list)],
        "npc_mix": [NPCMix.model_validate(item) for item in load_dataset("npc_mix", factory=list)],
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
        "trade_nodes": [TradeNode.model_validate(item) for item in load_dataset("trade_nodes", factory=list)],
        "trade_routes": [TradeRoute.model_validate(item) for item in load_dataset("trade_routes", factory=list)],
        "festivals": [Festival.model_validate(item) for item in load_dataset("festivals", factory=list)],
        "faction_presence": [
            FactionPresence.model_validate(item) for item in load_dataset("faction_presence", factory=list)
        ],
        "hostility": [Hostility.model_validate(item) for item in load_dataset("hostility", factory=list)],
        "access_rules": [AccessRule.model_validate(item) for item in load_dataset("access_rules", factory=list)],
        "law_params": LawCrimeParams.model_validate(law_data) if law_data else None,
        "district_crime": [
            DistrictCrimeOverride.model_validate(item) for item in load_dataset("district_crime", factory=list)
        ],
        "tuning": Tuning.model_validate(tuning_data) if tuning_data else None,
    }


def _poi_lookup(pois: Sequence[POI]) -> Dict[str, str]:
    return {poi.id: poi.properties.name for poi in pois}


def validate_world(state: Optional[WorldState] = None, min_event_age: int = 10) -> List[str]:
    """Run AAA rulebook validation and return textual issues."""

    state = state or _load_world_state()
    city: City | None = state.get("city")  # type: ignore[assignment]
    districts: Sequence[District] = state.get("districts", [])  # type: ignore[assignment]
    persons = {person.person_id: person for person in state["persons"]}  # type: ignore[index]
    households: Sequence[Household] = state["households"]  # type: ignore[assignment]
    events: Sequence[Event] = state["events"]  # type: ignore[assignment]
    quests: Sequence[Quest] = state["quests"]  # type: ignore[assignment]
    arcs: Sequence[StoryArc] = state["story_arcs"]  # type: ignore[assignment]
    zones: Sequence[MonsterZone] = state["monster_zones"]  # type: ignore[assignment]
    features: Sequence[GameplayFeature] = state["features"]  # type: ignore[assignment]
    items: Sequence[Item] = state["items"]  # type: ignore[assignment]
    activities: Sequence[Activity] = state["activities"]  # type: ignore[assignment]
    pois: Sequence[POI] = state["pois"]  # type: ignore[assignment]
    trade_nodes: Sequence[TradeNode] = state.get("trade_nodes", [])  # type: ignore[assignment]
    trade_routes: Sequence[TradeRoute] = state.get("trade_routes", [])  # type: ignore[assignment]
    festivals: Sequence[Festival] = state.get("festivals", [])  # type: ignore[assignment]
    faction_presence: Sequence[FactionPresence] = state.get("faction_presence", [])  # type: ignore[assignment]
    hostility_entries: Sequence[Hostility] = state.get("hostility", [])  # type: ignore[assignment]
    access_rules: Sequence[AccessRule] = state.get("access_rules", [])  # type: ignore[assignment]
    law_params: LawCrimeParams | None = state.get("law_params")  # type: ignore[assignment]
    district_overrides: Sequence[DistrictCrimeOverride] = state.get("district_crime", [])  # type: ignore[assignment]
    tuning: Tuning | None = state.get("tuning")  # type: ignore[assignment]
    poi_name = _poi_lookup(pois)
    hub_ids = [poi.id for poi in pois if "hub" in poi.properties.layers]

    issues: List[str] = []

    district_by_id: Dict[str, District] = {district.district_id: district for district in districts}

    if city:
        total_population = sum(d.population for d in districts)
        if city.population_target and abs(total_population - city.population_target) > city.population_target * 0.02:
            issues.append(
                f"Dân số các quận ({total_population}) lệch khỏi mục tiêu thành phố {city.population_target}"
            )
        for district in districts:
            if district.population > district.population_cap + 1:
                issues.append(
                    f"Quận {district.district_id} vượt sức chứa ({district.population} > {district.population_cap:.0f})"
                )

    mix_totals: Dict[str, float] = defaultdict(float)
    for entry in npc_mix:
        mix_totals[entry.district_id] += entry.ratio
    for district in districts:
        total = mix_totals.get(district.district_id, 0.0)
        if abs(total - 1.0) > 0.05:
            issues.append(f"Tỷ lệ NPC ở quận {district.district_id} không chuẩn hoá (tổng {total:.2f})")

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

    # Trade & food balance
    node_lookup = {node.node_id: node for node in trade_nodes}

    def node_population(node_id: str) -> float:
        node = node_lookup.get(node_id)
        if node and node.district_id in district_by_id:
            return district_by_id[node.district_id].population
        return 20000.0

    def dominant_terrain(route: TradeRoute) -> str:
        if not route.terrain_share:
            return "road"
        return max(route.terrain_share, key=route.terrain_share.get)

    food_required = 0.0
    food_imported = 0.0
    if city and tuning:
        food_required = city.population_target * tuning.food_per_capita
        for route in trade_routes:
            distance = max(route.distance_km, 1.0)
            pop_from = node_population(route.from_node_id)
            pop_to = node_population(route.to_node_id)
            flow_index = (pop_from * pop_to) / (distance ** 2)
            modifier = tuning.import_factor.get(dominant_terrain(route), 1.0)
            food_imported += flow_index * modifier
        if food_required > 0 and food_imported < food_required:
            issues.append(
                f"Thành phố thiếu lương thực ({food_imported:.0f} < {food_required:.0f})"
            )
    deficit_frac = max(0.0, 1 - (food_imported / food_required)) if food_required else 0.0

    # Festival modifiers
    guard_bonus: Dict[str, float] = defaultdict(float)
    crime_bonus: Dict[str, float] = defaultdict(float)
    for festival in festivals:
        targets = [festival.primary_zone, *festival.secondary_zones]
        for zone in targets:
            guard_bonus[zone] += festival.effects.guard_shift
            crime_bonus[zone] += festival.effects.crime_shift

    override_lookup = {override.district_id: override for override in district_overrides}
    capacity_by_district: Dict[str, int] = defaultdict(int)
    for poi in pois:
        capacity_by_district[poi.district_id] += poi.properties.capacity

    rule_ids = {rule.access_rule_id for rule in access_rules if rule.access_rule_id}

    if law_params and tuning:
        alpha = tuning.crime_coeffs.get("alphaLaw", 0.3)
        beta = tuning.crime_coeffs.get("betaPoverty", 0.2)
        gamma = tuning.crime_coeffs.get("gammaHotspot", 0.2)
        delta = tuning.crime_coeffs.get("deltaGuard", 0.5)
        for district in districts:
            overrides = override_lookup.get(district.district_id)
            hotspot_boost = 1.0 if overrides and (overrides.hotspot or overrides.black_market_flag) else 0.0
            guard_cov = max(0.0, min(1.0, district.guard_coverage_base + guard_bonus[district.district_id]))
            crime_base = district.crime_base + crime_bonus[district.district_id]
            crime_expected = max(
                0.0,
                min(
                    1.0,
                    crime_base
                    + alpha * (1 - law_params.lawfulness_base)
                    + beta * deficit_frac
                    + gamma * hotspot_boost
                    - delta * guard_cov,
                ),
            )
            guard_need = int((crime_expected * district.population) / max(1.0, law_params.guard_effectiveness) + 0.999)
            if district.type in {"Market", "Wharf"} and guard_cov < 0.3:
                issues.append(f"Quận {district.district_id} thiếu lực lượng canh gác (coverage {guard_cov:.2f})")
            if district.type == "Citadel" and guard_cov < 0.5:
                issues.append("Khu Hoàng thành cần tăng bảo vệ")
            if guard_need > guard_cov * district.population:
                issues.append(
                    f"Quận {district.district_id} cần {guard_need} lính nhưng coverage hiện chỉ {guard_cov:.2f}"
                )
            if law_params.high_crime_threshold and crime_expected > law_params.high_crime_threshold:
                issues.append(f"Quận {district.district_id} đang ở mức tội phạm {crime_expected:.2f} vượt ngưỡng")

            target_capacity = max(150, int(district.population * 0.1))
            if capacity_by_district[district.district_id] < target_capacity:
                issues.append(
                    f"POI quận {district.district_id} chưa đủ sức chứa (cần {target_capacity}, hiện {capacity_by_district[district.district_id]})"
                )

    for poi in pois:
        if poi.properties.access_rule_id and poi.properties.access_rule_id not in rule_ids:
            issues.append(
                f"POI {poi.properties.name} yêu cầu rule {poi.properties.access_rule_id} nhưng rule chưa tồn tại"
            )

    seen_slots: Dict[tuple[str, int, int], str] = {}
    for festival in festivals:
        targets = [festival.primary_zone, *festival.secondary_zones]
        for zone in targets:
            key = (zone, festival.month, festival.day)
            if key in seen_slots:
                issues.append(
                    f"Lễ hội {festival.name} trùng lịch với {seen_slots[key]} tại {zone} ngày {festival.month}/{festival.day}"
                )
            else:
                seen_slots[key] = festival.name

    for presence in faction_presence:
        if presence.influence < 0 or presence.influence > 100:
            issues.append(f"Ảnh hưởng {presence.faction_id} tại {presence.district_id} vượt biên ({presence.influence})")

    hostility_map: Dict[tuple[str, str], int] = {}
    for entry in hostility_entries:
        hostility_map[(entry.faction_a, entry.faction_b)] = entry.value
        if entry.value < -100 or entry.value > 100:
            issues.append(f"Quan hệ {entry.faction_a}/{entry.faction_b} ngoài biên độ ({entry.value})")
    for (a, b), value in hostility_map.items():
        reverse = hostility_map.get((b, a))
        if reverse is not None and abs(reverse - value) > 10:
            issues.append(f"Quan hệ {a}/{b} không đối xứng ({value} vs {reverse})")

    for route in trade_routes:
        share_sum = sum(route.terrain_share.values())
        if abs(share_sum - 1.0) > 0.05:
            issues.append(f"Tuyến {route.route_id} có phân bổ địa hình sai ({share_sum:.2f})")

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

    city: City | None = state.get("city")  # type: ignore[assignment]
    districts: Sequence[District] = state.get("districts", [])  # type: ignore[assignment]
    npc_mix: Sequence[NPCMix] = state.get("npc_mix", [])  # type: ignore[assignment]
    pois: Sequence[POI] = state["pois"]  # type: ignore[assignment]
    arcs: Sequence[StoryArc] = state["story_arcs"]  # type: ignore[assignment]
    features: Sequence[GameplayFeature] = state["features"]  # type: ignore[assignment]
    activities: Sequence[Activity] = state["activities"]  # type: ignore[assignment]
    zones: Sequence[MonsterZone] = state["monster_zones"]  # type: ignore[assignment]
    items: Sequence[Item] = state["items"]  # type: ignore[assignment]
    trade_routes: Sequence[TradeRoute] = state.get("trade_routes", [])  # type: ignore[assignment]
    trade_nodes: Sequence[TradeNode] = state.get("trade_nodes", [])  # type: ignore[assignment]
    festivals: Sequence[Festival] = state.get("festivals", [])  # type: ignore[assignment]
    faction_presence: Sequence[FactionPresence] = state.get("faction_presence", [])  # type: ignore[assignment]
    hostility_entries: Sequence[Hostility] = state.get("hostility", [])  # type: ignore[assignment]
    law_params: LawCrimeParams | None = state.get("law_params")  # type: ignore[assignment]
    district_overrides: Sequence[DistrictCrimeOverride] = state.get("district_crime", [])  # type: ignore[assignment]
    tuning: Tuning | None = state.get("tuning")  # type: ignore[assignment]

    poi_lookup = {poi.id: poi for poi in pois}
    hub_ids = [poi.id for poi in pois if "hub" in poi.properties.layers]
    hub_total = max(1, len(hub_ids))

    coverage_hubs = {hub for arc in arcs for hub in arc.coverage_hubs}
    story_coverage = round(len(coverage_hubs.intersection(hub_ids)) / hub_total * 100, 2)

    features_by_hub: Dict[str, set[str]] = defaultdict(set)
    for feature in features:
        features_by_hub[feature.poi_id].add(feature.feature_type)
    feature_ready = sum(1 for hub in hub_ids if ESSENTIAL_FEATURES.issubset(features_by_hub.get(hub, set())))
    feature_coverage = round(feature_ready / hub_total * 100, 2)

    activity_ready = sum(1 for hub in hub_ids if any(activity.poi_id == hub for activity in activities))
    activity_coverage = round(activity_ready / hub_total * 100, 2)

    style_counter = Counter()
    for zone in zones:
        for encounter in zone.encounters:
            style_counter[encounter.style] += 1
    variety_score = round(min(1.0, sum(1 for style in VARIETY_STYLES if style_counter[style]) / len(VARIETY_STYLES)) * 100, 2)
    encounter_breakdown = {
        style: round(style_counter[style] / max(1, sum(style_counter.values())) * 100, 2)
        for style in VARIETY_STYLES
    }

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

    # City metrics
    terrain_speed = {"river": 14.0, "plains": 10.0, "hill": 6.0, "mountain": 4.0, "swamp": 5.0}
    node_lookup = {node.node_id: node for node in trade_nodes}
    district_by_id = {district.district_id: district for district in districts}

    def node_population(node_id: str) -> float:
        node = node_lookup.get(node_id)
        if node and node.district_id in district_by_id:
            return district_by_id[node.district_id].population
        return 20000.0

    def dominant_terrain(route: TradeRoute) -> str:
        if not route.terrain_share:
            return "road"
        return max(route.terrain_share, key=route.terrain_share.get)

    food_required = 0.0
    food_imported = 0.0
    if city and tuning:
        food_required = city.population_target * tuning.food_per_capita
        for route in trade_routes:
            distance = max(route.distance_km, 1.0)
            pop_from = node_population(route.from_node_id)
            pop_to = node_population(route.to_node_id)
            flow_index = (pop_from * pop_to) / (distance ** 2)
            modifier = tuning.import_factor.get(dominant_terrain(route), 1.0)
            food_imported += flow_index * modifier
    deficit_frac = max(0.0, 1 - (food_imported / food_required)) if food_required else 0.0
    food_balance = food_imported - food_required

    kappa = 0.5
    price_index = 1.0 + deficit_frac * kappa
    if tuning:
        price_index = max(tuning.price_index_clamp.get("min", 0.5), min(price_index, tuning.price_index_clamp.get("max", 1.5)))

    # Stability calculation
    court_inf = next((p.influence for p in faction_presence if p.faction_id == "Court" and p.district_id == "CITADEL"), 0)
    rebel_inf = [
        p.influence
        for p in faction_presence
        if p.faction_id == "Rebels" and p.district_id in {"WHARF", "MARKET_EAST"}
    ]
    rebel_avg = sum(rebel_inf) / len(rebel_inf) if rebel_inf else 0
    surplus_pct = 100 * (food_imported / max(1.0, food_required)) - 100 if food_required else 0
    stability = 60 + min(20, surplus_pct / 5) + 1.5 * (court_inf / 10) - 1.5 * (rebel_avg / 10)
    stability = max(0.0, min(100.0, stability))

    # Crime analytics
    guard_bonus: Dict[str, float] = defaultdict(float)
    crime_bonus: Dict[str, float] = defaultdict(float)
    for festival in festivals:
        targets = [festival.primary_zone, *festival.secondary_zones]
        for zone in targets:
            guard_bonus[zone] += festival.effects.guard_shift
            crime_bonus[zone] += festival.effects.crime_shift

    override_lookup = {override.district_id: override for override in district_overrides}
    district_snapshots: Dict[str, Dict[str, float]] = {}
    guard_need_total = 0
    crime_total = 0.0
    for district in districts:
        overrides = override_lookup.get(district.district_id)
        hotspot_boost = 1.0 if overrides and (overrides.hotspot or overrides.black_market_flag) else 0.0
        guard_cov = district.guard_coverage_base + guard_bonus[district.district_id]
        guard_cov = max(0.0, min(1.0, guard_cov))
        crime_base = district.crime_base + crime_bonus[district.district_id]
        alpha = tuning.crime_coeffs.get("alphaLaw", 0.3) if tuning else 0.3
        beta = tuning.crime_coeffs.get("betaPoverty", 0.2) if tuning else 0.2
        gamma = tuning.crime_coeffs.get("gammaHotspot", 0.2) if tuning else 0.2
        delta = tuning.crime_coeffs.get("deltaGuard", 0.5) if tuning else 0.5
        lawfulness = law_params.lawfulness_base if law_params else 0.6
        crime_expected = crime_base + alpha * (1 - lawfulness) + beta * deficit_frac + gamma * hotspot_boost - delta * guard_cov
        crime_expected = max(0.0, min(1.0, crime_expected))
        guard_effectiveness = law_params.guard_effectiveness if law_params else 400
        guard_need = int((crime_expected * district.population) / max(1.0, guard_effectiveness) + 0.999)
        guard_need_total += guard_need
        crime_total += crime_expected
        capacity_target = max(150, int(district.population * 0.1))
        capacity_actual = sum(
            poi.properties.capacity for poi in pois if poi.district_id == district.district_id
        )
        district_snapshots[district.district_id] = {
            "population": district.population,
            "crime_expected": round(crime_expected, 3),
            "guard_coverage": round(guard_cov, 3),
            "guard_need": guard_need,
            "capacity": capacity_actual,
            "capacity_target": capacity_target,
            "hotspot": 1.0 if hotspot_boost else 0.0,
        }

    crime_avg = round(crime_total / max(1, len(districts)), 3)

    # Coverage matrix (quest/vendor/guard/event)
    coverage_matrix: Dict[str, Dict[str, object]] = {}
    poi_to_district = {poi.id: poi.district_id for poi in pois}
    quest_coverage: Dict[str, set[str]] = defaultdict(set)
    for arc in arcs:
        for hub in arc.coverage_hubs:
            district_id = poi_to_district.get(hub)
            if district_id:
                quest_coverage[district_id].add(arc.arc_id)
    vendor_count: Dict[str, int] = defaultdict(int)
    for poi in pois:
        if "Vendor" in {service.title() for service in poi.properties.services} or "Vendor" in poi.properties.services:
            vendor_count[poi.district_id] += 1
    festival_count: Dict[str, int] = defaultdict(int)
    for festival in festivals:
        festival_count[festival.primary_zone] += 1
        for zone in festival.secondary_zones:
            festival_count[zone] += 1
    for district in districts:
        snapshot = district_snapshots.get(district.district_id, {})
        coverage_matrix[district.district_id] = {
            "quests": len(quest_coverage.get(district.district_id, set())),
            "vendors": vendor_count.get(district.district_id, 0),
            "guard_ready": snapshot.get("guard_coverage", 0) >= 0.3,
            "events": festival_count.get(district.district_id, 0),
        }

    # Trade summary
    trade_summary: List[Dict[str, object]] = []
    for route in trade_routes:
        share_sum = sum(route.terrain_share.values())
        trade_summary.append(
            {
                "route_id": route.route_id,
                "dominant": dominant_terrain(route),
                "distance_km": route.distance_km,
                "terrain_sum": round(share_sum, 2),
            }
        )

    # Faction matrices
    faction_matrix: Dict[str, Dict[str, int]] = defaultdict(dict)
    for presence in faction_presence:
        faction_matrix[presence.faction_id][presence.district_id] = presence.influence
    hostility_matrix: Dict[str, Dict[str, int]] = defaultdict(dict)
    for entry in hostility_entries:
        hostility_matrix[entry.faction_a][entry.faction_b] = entry.value

    schedule_overview: Dict[str, List[str]] = defaultdict(list)
    for activity in activities:
        schedule_overview[activity.schedule.cadence].append(activity.name)

    export_ready = 100.0 if not issues else max(0.0, 100.0 - len(issues) * 5)

    dataset_counts = {key: len(value) if isinstance(value, list) else 1 for key, value in state.items() if key not in {"law_params", "tuning", "city"}}

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
        "city_overview": {
            "population_target": city.population_target if city else None,
            "food_required": round(food_required, 2),
            "food_imported": round(food_imported, 2),
            "food_balance": round(food_balance, 2),
            "deficit_frac": round(deficit_frac, 3),
            "price_index": round(price_index, 3),
            "stability": round(stability, 2),
            "crime_average": crime_avg,
            "guard_need_total": guard_need_total,
            "active_festivals": len(festivals),
        },
        "districts": district_snapshots,
        "coverage_matrix": coverage_matrix,
        "trade_summary": trade_summary,
        "faction_matrix": faction_matrix,
        "hostility_matrix": hostility_matrix,
        "dataset_counts": dataset_counts,
    }

