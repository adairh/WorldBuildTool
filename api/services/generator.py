"""Procedural generators for TL-Forge."""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence

try:  # pragma: no cover - faker is optional during doc builds
    from faker import Faker
except Exception:  # pragma: no cover
    Faker = None

from ..schemas import (
    Asset,
    EconomySnapshot,
    Event,
    Household,
    HouseholdLedger,
    MartialStyle,
    NarrativeHook,
    Person,
    POI,
    Quest,
    QuestChoice,
    QuestNode,
    Relationship,
    Trait,
    WorldBundle,
    WorldRequest,
)

_CURRENT_YEAR = 1285
_DISTRICTS = [
    "Đại La",
    "Long Thành",
    "Thăng Long Citadel",
    "Nhật Tân",
    "Lĩnh Nam",
    "Bát Tràng",
    "Hội An Guild Quarter",
]
_SPECIALTIES = [
    "silk merchants",
    "jade sculptors",
    "tea horticulturists",
    "martial tutors",
    "royal scribes",
    "river wardens",
    "shadow couriers",
]
_ALLEGIANCES = [
    "Imperial Court",
    "Trần Dynasty",
    "Thanh Long Sect",
    "Vũ Lâm Amazon Guard",
    "Nghệ An Rebels",
    "Blackened Lotus",
]
_REPUTATIONS = [
    "venerated",
    "notorious",
    "mysterious",
    "beloved",
    "shadowed",
    "ascendant",
]
_MARTIAL_STYLES = [
    {"name": "Long Kiếm Pháp", "element": "water", "hallmarkMove": "Dragon Current Reversal"},
    {"name": "Hạc Tụ Quyền", "element": "wind", "hallmarkMove": "Crane Eclipse Swoop"},
    {"name": "Huyền Hỏa Chưởng", "element": "fire", "hallmarkMove": "Profane Lotus Bloom"},
    {"name": "Thiết Sơn Cương", "element": "earth", "hallmarkMove": "Titan's Rolling Advance"},
    {"name": "Nguyệt Ảnh Bộ", "element": "shadow", "hallmarkMove": "Moonstep Mirage"},
]
_TRAIT_LIBRARY = [
    ("Long Bloodline", "Rumored descendent of sea dragons governing {district}"),
    ("Azure Scholar", "Maintains a forbidden archive for {clan}"),
    ("Ghost Voice", "Can mimic ancestors after moonrise"),
    ("Jade Vision", "Sees the flow of qi around market stalls"),
    ("Storm Scar", "Survived a heavenly lightning strike"),
    ("Tea Whisperer", "Brews infusions that reveal lost memories"),
    ("Shadow Pact", "Once struck a bargain with the Blackened Lotus"),
]
_PROFESSIONS = [
    "merchant",
    "alchemist",
    "scribe",
    "sword dancer",
    "river warden",
    "strategist",
    "shadow agent",
    "historian",
]
_CULTIVATION_STAGES = [
    "Mortal Foundation",
    "Qi Initiate",
    "Inner Meridian",
    "Golden Core",
    "Nascent Soul",
]
_SEASONS = ["Xuân", "Hạ", "Thu", "Đông"]
_EVENT_TYPES = [
    "martial tournament",
    "night market intrigue",
    "spirit festival",
    "sect summit",
    "imperial edict",
    "river beast hunt",
]
_EVENT_OUTCOMES = [
    "forged an unexpected alliance",
    "ignited a blood feud",
    "revealed an ancient artifact",
    "sealed a spirit gate",
    "shifted guild balances",
    "toppled a rival patron",
]
_QUEST_TONES = ["heroic", "tragic", "mystical", "political", "exploratory"]
_REWARD_LIBRARY = [
    "rare jade focus",
    "imperial favor",
    "martial technique scroll",
    "underground trade routes",
    "ancestral blessing",
]
_GUILD_REPORTS = {
    "Silk Syndicate": "Profits surge as royal court seeks ceremonial robes.",
    "River Coalition": "Water levels unpredictable; wardens request qi reinforcements.",
    "Wayfarer League": "Whispers of a hidden gateway beneath Bạch Đằng.",
}

if Faker is not None:
    _faker = Faker("vi_VN")
else:  # pragma: no cover - fallback for docs environments
    _faker = None


def _fake_name(rng: random.Random, sex: str) -> str:
    if _faker is None:
        token = rng.randint(100, 999)
        return f"Nhân vật-{sex}-{token}"
    _faker.seed_instance(rng.randint(0, 999_999))
    if sex == "F":
        return _faker.name_female()
    if sex == "NB":
        # Faker doesn't ship neutral Vietnamese names, pick from dataset manually
        name = rng.choice(["Bình", "Khánh", "Minh", "An", "Trúc"])
        surname = rng.choice(["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng"])
        return f"{surname} {name}"
    return _faker.name_male()


def _courtesy_name(rng: random.Random) -> str:
    syllables = ["Thanh", "Liên", "Vân", "Phong", "Nguyệt", "Tịnh", "Hạo", "Chi"]
    return f"{rng.choice(syllables)} {rng.choice(syllables)}"


def _generate_traits(rng: random.Random, clan: str, district: str) -> List[Trait]:
    traits: List[Trait] = []
    count = rng.randint(1, 2)
    for name, template in rng.sample(_TRAIT_LIBRARY, count):
        traits.append(Trait(name=name, description=template.format(clan=clan, district=district)))
    return traits


def _relationship(source: Person, target: Person, relation: str, intensity: int) -> Relationship:
    return Relationship(targetId=target.id, relation=relation, intensity=intensity)


def generate_households(
    count: int = 10,
    seed: int = 42,
    rng: Optional[random.Random] = None,
) -> List[Household]:
    """Generate a roster of complex households."""

    rng = rng or random.Random(seed)
    households: List[Household] = []

    for index in range(count):
        clan = rng.choice(["Nguyễn", "Trần", "Phạm", "Lê", "Đặng", "Vũ"])
        district = rng.choice(_DISTRICTS)
        specialty = rng.choice(_SPECIALTIES)
        allegiance = rng.choice(_ALLEGIANCES)
        reputation = rng.choice(_REPUTATIONS)
        members: List[Person] = []

        household_id = f"HH-{seed:02d}-{index:03d}"
        member_count = rng.randint(3, 6)

        for member_idx in range(member_count):
            sex = rng.choice(["M", "F", "F", "M", "NB"])
            age = rng.randint(18, 60)
            birth_year = _CURRENT_YEAR - age
            person_id = f"P-{household_id}-{member_idx:02d}"
            courtesy_name = _courtesy_name(rng)
            style_data = rng.choice(_MARTIAL_STYLES)
            martial_style = MartialStyle(**style_data)
            profession = rng.choice(_PROFESSIONS)
            traits = _generate_traits(rng, clan, district)
            cultivation_stage = rng.choice(_CULTIVATION_STAGES)

            person = Person(
                id=person_id,
                name=_fake_name(rng, sex),
                courtesyName=courtesy_name,
                birthYear=birth_year,
                sex=sex,
                profession=profession,
                cultivationStage=cultivation_stage,
                martialStyle=martial_style,
                notableTraits=traits,
                householdId=household_id,
                homePoiId=None,
                relationships=[],
            )
            members.append(person)

        # bind relationships: first member mentors rest, adjacency as siblings
        if members:
            head = members[0]
            for follower in members[1:]:
                head.relationships.append(_relationship(head, follower, "mentor", 4))
                follower.relationships.append(_relationship(follower, head, "mentor", 3))

        for a, b in zip(members[1:], members[2:]):
            a.relationships.append(_relationship(a, b, "sibling", 2))
            b.relationships.append(_relationship(b, a, "sibling", 2))

        ledger = HouseholdLedger(
            silver=rng.randint(1_000, 8_500),
            rice=rng.randint(200, 2_000),
            artisans=rng.randint(2, 12),
            renown=rng.randint(30, 95),
        )

        founding_legend = (
            f"Founded when {clan} emissaries brokered a pact with river spirits at {district}."
        )
        assets = [
            f"seal of {clan}",
            f"{rng.choice(['jade', 'obsidian', 'bronze'])} {specialty} toolkit",
        ]

        alliances = rng.sample(_ALLEGIANCES, k=min(2, len(_ALLEGIANCES)))
        rivals = [al for al in _ALLEGIANCES if al not in alliances]
        rng.shuffle(rivals)

        household = Household(
            id=household_id,
            name=f"{clan} {specialty.title()}",
            clan=clan,
            district=district,
            specialty=specialty,
            allegiance=allegiance,
            reputation=reputation,
            foundingLegend=founding_legend,
            members=members,
            alliances=alliances[:2],
            rivals=rivals[:2],
            assets=assets,
            ledger=ledger,
        )
        households.append(household)

    return households


def _flatten_members(households: Sequence[Household]) -> List[Person]:
    return [member for household in households for member in household.members]


def generate_pois(
    households: Sequence[Household],
    seed: int,
    count: Optional[int] = None,
) -> List[POI]:
    rng = random.Random(seed + 11)
    count = count or max(6, len(households) * 2)
    pois: List[POI] = []
    templates = [
        ("Guildhall", "Hội quán của {clan} oversee trade of {specialty}"),
        ("Spirit Shrine", "Shrine honoring river dragons protecting {district}"),
        ("Hidden Teahouse", "Secret meeting spot for {allegiance} envoys"),
        ("Training Yard", "Disciples refine {style} forms under moonlight"),
        ("Floating Market", "Merchants hawk mystical wares across wooden barges"),
    ]
    for idx in range(count):
        household = rng.choice(households)
        template = rng.choice(templates)
        name = f"{household.clan} {template[0]} #{idx:02d}"
        description = template[1].format(
            clan=household.clan,
            specialty=household.specialty,
            district=household.district,
            allegiance=household.allegiance,
            style=rng.choice(_MARTIAL_STYLES)["name"],
        )
        poi = POI(
            id=f"POI-{seed:02d}-{idx:03d}",
            name=name,
            category=template[0],
            district=household.district,
            description=description,
            layers={
                "elevation": rng.choice(["lowland", "citadel terrace", "riverbank"]),
                "qi_flow": rng.choice(["tranquil", "tempestuous", "veiled"]),
            },
            tags=[household.clan, household.specialty],
        )
        pois.append(poi)

    return pois


def generate_events(
    persons: Sequence[Person],
    pois: Sequence[POI],
    seed: int,
    count: int,
) -> List[Event]:
    rng = random.Random(seed + 23)
    events: List[Event] = []
    for idx in range(count):
        participants = rng.sample(persons, k=min(len(persons), rng.randint(2, 5)))
        poi = rng.choice(pois) if pois else None
        event_type = rng.choice(_EVENT_TYPES)
        outcome = rng.choice(_EVENT_OUTCOMES)
        repercussions = [
            f"{rng.choice(_ALLEGIANCES)} {rng.choice(['gains', 'loses'])} influence",
            f"Rumors of {rng.choice(['ancient tomb', 'divine trial', 'lost heir'])}",
        ]
        title = f"{event_type.title()} of {participants[0].courtesyName}" if participants else event_type
        event = Event(
            id=f"EV-{seed:02d}-{idx:03d}",
            year=_CURRENT_YEAR + rng.randint(-4, 4),
            season=rng.choice(_SEASONS),
            title=title,
            description=f"A {event_type} that {outcome}.",
            primaryPoiId=poi.id if poi else None,
            participantIds=[p.id for p in participants],
            type=event_type,
            outcome=outcome,
            repercussions=repercussions,
        )
        events.append(event)
    return events


def _quest_nodes(
    rng: random.Random,
    quest_id: str,
    patron: Household,
    featured_event: Event,
    highlight_person: Person,
) -> Dict[str, QuestNode]:
    intro_id = f"{quest_id}-N0"
    duel_id = f"{quest_id}-N1"
    intrigue_id = f"{quest_id}-N2"

    intro_node = QuestNode(
        id=intro_id,
        speaker=patron.members[0].name,
        dialogue=(
            f"{patron.clan} requests aid: rumors say the {featured_event.title.lower()} "
            f"conceals a traitor bound to the {patron.allegiance}."
        ),
        cinematicCue="Camera pans across jade lanterns and hidden blades.",
        choices=[
            QuestChoice(
                id=f"{quest_id}-C0",
                text="Investigate the night market dens",
                skillCheck="Insight 3",
                nextNodeId=duel_id,
                reputationShift={patron.id: 2},
                rewards=[rng.choice(_REWARD_LIBRARY)],
            ),
            QuestChoice(
                id=f"{quest_id}-C1",
                text=f"Confront {highlight_person.courtesyName} directly",
                skillCheck="Combat 4",
                nextNodeId=intrigue_id,
                reputationShift={patron.id: -1},
                rewards=["secret moonlight technique"],
            ),
        ],
    )

    duel_node = QuestNode(
        id=duel_id,
        speaker=highlight_person.name,
        dialogue="Steel clashes over moonlit water as accusations surface.",
        choices=[
            QuestChoice(
                id=f"{quest_id}-C2",
                text="Spare the accused and forge an alliance",
                skillCheck="Diplomacy 4",
                nextNodeId=intrigue_id,
                reputationShift={patron.id: 1},
                rewards=["pledged river patrols"],
            ),
            QuestChoice(
                id=f"{quest_id}-C3",
                text="Deliver ruthless judgment",
                skillCheck="Ferocity 5",
                nextNodeId=None,
                reputationShift={patron.id: -3},
                rewards=["artifact shard"],
            ),
        ],
    )

    intrigue_node = QuestNode(
        id=intrigue_id,
        speaker=None,
        dialogue=(
            "Spies expose the conspiracy's architect; the palace drums begin to roll."
        ),
        choices=[
            QuestChoice(
                id=f"{quest_id}-C4",
                text="Swear loyalty to the {0}".format(patron.allegiance),
                skillCheck=None,
                nextNodeId=None,
                reputationShift={patron.id: 3},
                rewards=["dynasty favor"],
            ),
            QuestChoice(
                id=f"{quest_id}-C5",
                text="Use the chaos to empower your own sect",
                skillCheck="Guile 4",
                nextNodeId=None,
                reputationShift={patron.id: -2},
                rewards=["hidden vault access"],
            ),
        ],
    )

    return {intro_id: intro_node, duel_id: duel_node, intrigue_id: intrigue_node}


def generate_quests(
    households: Sequence[Household],
    events: Sequence[Event],
    persons: Sequence[Person],
    seed: int,
    count: int,
) -> List[Quest]:
    rng = random.Random(seed + 41)
    quests: List[Quest] = []
    for idx in range(count):
        if not households or not events or not persons:
            break
        patron = rng.choice(households)
        featured_event = rng.choice(events)
        highlight_person = rng.choice(persons)
        quest_id = f"QT-{seed:02d}-{idx:03d}"
        nodes = _quest_nodes(rng, quest_id, patron, featured_event, highlight_person)
        quest = Quest(
            id=quest_id,
            title=f"Echoes of {featured_event.title}",
            synopsis=(
                f"Investigate how {featured_event.title.lower()} disrupted {patron.clan}'s "
                f"standing within the {patron.allegiance}."
            ),
            startingNodeId=f"{quest_id}-N0",
            requiredReputation={patron.id: 20},
            nodes=nodes,
            rewards=rng.sample(_REWARD_LIBRARY, k=2),
            factionsInvolved=[patron.allegiance, featured_event.type],
        )
        quests.append(quest)
    return quests


def generate_assets(
    households: Sequence[Household],
    quests: Sequence[Quest],
    seed: int,
) -> List[Asset]:
    rng = random.Random(seed + 59)
    assets: List[Asset] = []
    for household in households:
        assets.append(
            Asset(
                id=f"AST-{household.id}",
                name=f"{household.clan} crest",
                category="emblem",
                prompt=(
                    f"Illustrate an ornate {household.clan} crest featuring {household.specialty} motifs "
                    f"within {household.district}."
                ),
                storagePath=f"households/{household.id}/crest.png",
                attribution="Procedurally generated by TL-Forge",
            )
        )
    for quest in quests:
        assets.append(
            Asset(
                id=f"AST-{quest.id}",
                name=f"Storyboard - {quest.title}",
                category="storyboard",
                prompt=f"Storyboard the pivotal confrontation from quest {quest.id}.",
                storagePath=f"quests/{quest.id}/storyboard.png",
                attribution=None,
            )
        )
    return assets


def derive_economy(households: Sequence[Household], seed: int) -> EconomySnapshot:
    rng = random.Random(seed + 71)
    total_silver = sum(h.ledger.silver for h in households)
    total_rice = sum(h.ledger.rice for h in households)
    artisan_count = sum(h.ledger.artisans for h in households)
    reputation_averages: Dict[str, float] = {}
    for allegiance in _ALLEGIANCES:
        relevant = [h.ledger.renown for h in households if allegiance in h.alliances]
        reputation_averages[allegiance] = round(sum(relevant) / len(relevant), 2) if relevant else 0.0
    guild_reports = {
        guild: report + f" Forecast confidence {rng.randint(60, 98)}%."
        for guild, report in _GUILD_REPORTS.items()
    }
    return EconomySnapshot(
        year=_CURRENT_YEAR,
        totalSilver=total_silver,
        totalRice=total_rice,
        artisanCount=artisan_count,
        reputationAverages=reputation_averages,
        guildReports=guild_reports,
    )


def generate_hooks(
    quests: Sequence[Quest],
    events: Sequence[Event],
    seed: int,
) -> List[NarrativeHook]:
    rng = random.Random(seed + 83)
    hooks: List[NarrativeHook] = []
    for idx, quest in enumerate(quests[:8]):
        event = rng.choice(events) if events else None
        tone = rng.choice(_QUEST_TONES)
        pitch = (
            f"When {quest.title} unfolds, the balance of the {tone} factions in Thăng Long shifts."
        )
        if event:
            pitch += f" The fallout of {event.title} still echoes through the alleys."
        hooks.append(
            NarrativeHook(
                id=f"HOOK-{seed:02d}-{idx:02d}",
                title=f"{tone.title()} Tides",
                pitch=pitch,
                suggestedQuestId=quest.id,
                tone=tone,
            )
        )
    return hooks


def generate_world(request: WorldRequest) -> WorldBundle:
    """Generate a full world bundle from request parameters."""

    households = generate_households(request.household_count, seed=request.seed)
    persons = _flatten_members(households)
    pois = generate_pois(households, seed=request.seed)
    events = generate_events(persons, pois, seed=request.seed, count=request.event_count)
    quests = generate_quests(households, events, persons, seed=request.seed, count=request.quest_count)
    assets = generate_assets(households, quests, seed=request.seed) if request.include_assets else []
    economy = derive_economy(households, seed=request.seed)
    hooks = generate_hooks(quests, events, seed=request.seed)

    return WorldBundle(
        seed=request.seed,
        households=households,
        persons=persons,
        pois=pois,
        events=events,
        quests=quests,
        assets=assets,
        economy=economy,
        narrativeHooks=hooks,
    )


def summarize_world(bundle: WorldBundle) -> Dict[str, object]:
    """Produce a quick diagnostic summary for UI usage."""

    return {
        "seed": bundle.seed,
        "households": len(bundle.households),
        "persons": len(bundle.persons),
        "pois": len(bundle.pois),
        "events": len(bundle.events),
        "quests": len(bundle.quests),
        "assets": len(bundle.assets),
        "economy": {
            "totalSilver": bundle.economy.totalSilver,
            "totalRice": bundle.economy.totalRice,
            "artisanCount": bundle.economy.artisanCount,
        },
    }
