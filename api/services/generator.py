from __future__ import annotations

import random
from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, Iterable, List, Sequence, Tuple
from uuid import uuid4

from faker import Faker

from ..models import (
    AccessRequirements,
    AccessRule,
    Activity,
    ActivitySchedule,
    City,
    LevelBand,
    District,
    EncounterProfile,
    Festival,
    FestivalEffects,
    FactionPresence,
    GameplayFeature,
    Geometry,
    Household,
    HouseholdLedger,
    HouseholdLocation,
    Hostility,
    Item,
    LootSource,
    LawCrimeParams,
    DistrictCrimeOverride,
    MonsterZone,
    NPCMix,
    Person,
    POI,
    POIProperties,
    Quest,
    DialogueNode,
    StoryArc,
    StoryBeat,
    TradeNode,
    TradeRoute,
    Tuning,
    ReputationGate,
)
from .checker import ESSENTIAL_FEATURES
from ..storage import load_dataset, save_dataset

fake = Faker("vi_VN")

# --- Templates -----------------------------------------------------------------

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
    "Thư họa và kiếm pháp",
)

TUNING_DEFAULT = Tuning(
    food_per_capita=1.0,
    import_factor={"river": 1.2, "road": 0.9, "mountain": 0.6, "swamp": 0.7},
    crime_coeffs={"alphaLaw": 0.35, "betaPoverty": 0.3, "gammaHotspot": 0.2, "deltaGuard": 0.55},
    stability_thresholds={"warn": 55.0, "critical": 40.0},
    influence_drift={
        "muCourt": 0.6,
        "rhoRebel": 0.8,
        "tauMerchant": 0.7,
        "psiMonastic": 0.5,
        "chiSeizure": 0.4,
        "nuCorruption": 0.5,
    },
    gold_per_min=12.0,
    price_index_clamp={"min": 0.75, "max": 1.35},
)

DISTRICT_BLUEPRINTS: Sequence[Dict[str, object]] = (
    {
        "district_id": "CITADEL",
        "type": "Citadel",
        "footprint_area_km2": 0.45,
        "density_target": 12000,
        "population": 4052,
        "crime_base": 0.05,
        "guard_coverage_base": 0.8,
        "landmark_tags": ["royal", "approval"],
    },
    {
        "district_id": "MARKET_EAST",
        "type": "Market",
        "footprint_area_km2": 0.30,
        "density_target": 25000,
        "population": 5740,
        "crime_base": 0.22,
        "guard_coverage_base": 0.35,
        "landmark_tags": ["market", "festival"],
    },
    {
        "district_id": "MARKET_WEST",
        "type": "Market",
        "footprint_area_km2": 0.22,
        "density_target": 21000,
        "population": 3799,
        "crime_base": 0.18,
        "guard_coverage_base": 0.4,
        "landmark_tags": ["craft", "guild"],
    },
    {
        "district_id": "WHARF",
        "type": "Wharf",
        "footprint_area_km2": 0.35,
        "density_target": 18000,
        "population": 3292,
        "crime_base": 0.28,
        "guard_coverage_base": 0.3,
        "landmark_tags": ["river", "blackmarket"],
    },
    {
        "district_id": "ARTISAN_QTR",
        "type": "Artisan",
        "footprint_area_km2": 0.28,
        "density_target": 16000,
        "population": 2195,
        "crime_base": 0.12,
        "guard_coverage_base": 0.35,
        "landmark_tags": ["craft", "orders"],
    },
    {
        "district_id": "BARRACKS",
        "type": "Barracks",
        "footprint_area_km2": 0.20,
        "density_target": 15000,
        "population": 1519,
        "crime_base": 0.08,
        "guard_coverage_base": 0.85,
        "landmark_tags": ["military", "training"],
    },
    {
        "district_id": "TEMPLES",
        "type": "Temple",
        "footprint_area_km2": 0.25,
        "density_target": 14000,
        "population": 1604,
        "crime_base": 0.06,
        "guard_coverage_base": 0.3,
        "landmark_tags": ["ritual", "scholar"],
    },
    {
        "district_id": "RESIDENTIAL_N",
        "type": "Residential",
        "footprint_area_km2": 0.40,
        "density_target": 12000,
        "population": 2870,
        "crime_base": 0.14,
        "guard_coverage_base": 0.25,
        "landmark_tags": ["community", "vendor"],
    },
    {
        "district_id": "RESIDENTIAL_S",
        "type": "Residential",
        "footprint_area_km2": 0.25,
        "density_target": 10000,
        "population": 929,
        "crime_base": 0.1,
        "guard_coverage_base": 0.4,
        "landmark_tags": ["noble", "garden"],
    },
)

NPC_MIX_TABLE: Dict[str, Sequence[Tuple[str, float]]] = {
    "CITADEL": (
        ("Bureaucrat", 0.35),
        ("Guard", 0.35),
        ("Noble", 0.15),
        ("Monk", 0.05),
        ("Scholar", 0.05),
        ("Servant", 0.05),
    ),
    "MARKET_EAST": (
        ("Merchant", 0.38),
        ("Artisan", 0.22),
        ("Commoner", 0.22),
        ("Guard", 0.08),
        ("Thief", 0.05),
        ("Performer", 0.05),
    ),
    "MARKET_WEST": (
        ("Artisan", 0.3),
        ("Merchant", 0.3),
        ("Commoner", 0.2),
        ("Guard", 0.1),
        ("Thief", 0.05),
        ("Performer", 0.05),
    ),
    "WHARF": (
        ("Fisher", 0.22),
        ("Merchant", 0.18),
        ("Smuggler", 0.12),
        ("Commoner", 0.28),
        ("Guard", 0.08),
        ("Thief", 0.12),
    ),
    "ARTISAN_QTR": (
        ("Artisan", 0.45),
        ("Merchant", 0.15),
        ("Commoner", 0.25),
        ("Guard", 0.05),
        ("Scholar", 0.05),
        ("Beggar", 0.05),
    ),
    "BARRACKS": (
        ("Guard", 0.7),
        ("Recruit", 0.15),
        ("Trainer", 0.1),
        ("Merchant", 0.03),
        ("Healer", 0.02),
    ),
    "TEMPLES": (
        ("Scholar", 0.35),
        ("Monk", 0.3),
        ("Commoner", 0.2),
        ("Performer", 0.05),
        ("Merchant", 0.05),
        ("Guard", 0.05),
    ),
    "RESIDENTIAL_N": (
        ("Commoner", 0.6),
        ("Artisan", 0.15),
        ("Merchant", 0.05),
        ("Guard", 0.05),
        ("Beggar", 0.1),
        ("Performer", 0.05),
    ),
    "RESIDENTIAL_S": (
        ("Noble", 0.3),
        ("Servant", 0.3),
        ("Guard", 0.2),
        ("Monk", 0.05),
        ("Scholar", 0.1),
        ("Merchant", 0.05),
    ),
}

TRADE_NODE_BLUEPRINTS: Sequence[Tuple[str, str, str]] = (
    ("GATE_N", "CITADEL", "Gate"),
    ("GATE_E", "MARKET_EAST", "Gate"),
    ("GATE_W", "MARKET_WEST", "Gate"),
    ("GATE_S", "RESIDENTIAL_N", "Gate"),
    ("WHARF_TOLICH", "WHARF", "Wharf"),
    ("WHARF_NHIHA", "WHARF", "Wharf"),
)

TRADE_ROUTE_BLUEPRINTS: Sequence[Dict[str, object]] = (
    {
        "route_id": "RIVER_DELTA",
        "from_node_id": "RIVER_DELTA",
        "to_node_id": "WHARF_NHIHA",
        "distance_km": 38.0,
        "terrain_share": {"river": 1.0},
    },
    {
        "route_id": "VAN_KIEP",
        "from_node_id": "VAN_KIEP",
        "to_node_id": "GATE_N",
        "distance_km": 65.0,
        "terrain_share": {"plains": 0.6, "hill": 0.3, "river": 0.1},
    },
    {
        "route_id": "RICE_HEARTLAND",
        "from_node_id": "RICE_HEARTLAND",
        "to_node_id": "GATE_S",
        "distance_km": 52.0,
        "terrain_share": {"plains": 0.8, "swamp": 0.2},
    },
)

FESTIVAL_BLUEPRINTS: Sequence[Dict[str, object]] = (
    {
        "festival_id": "ROYAL_SPRING",
        "name": "Royal Spring Rite",
        "month": 1,
        "day": 5,
        "duration_days": 1,
        "primary_zone": "CITADEL",
        "theme": "Royal",
        "effects": {
            "vendor_boost_pct": 0.03,
            "guard_shift": 0.1,
            "price_delta_pct": 0.03,
            "quest_unlock_tags": ["Audience Petition"],
        },
    },
    {
        "festival_id": "LANTERN_FEST",
        "name": "Lantern Festival",
        "month": 1,
        "day": 15,
        "duration_days": 1,
        "primary_zone": "MARKET_EAST",
        "secondary_zones": ["TEMPLES"],
        "theme": "Lantern",
        "effects": {
            "vendor_boost_pct": 0.2,
            "crime_shift": 0.1,
            "guard_shift": 0.05,
            "spawn_overrides": ["pickpocket"],
            "quest_unlock_tags": ["LanternQuest"],
        },
    },
    {
        "festival_id": "DRAGON_BOAT",
        "name": "Dragon Boat Races",
        "month": 5,
        "day": 10,
        "duration_days": 1,
        "primary_zone": "WHARF",
        "theme": "River",
        "effects": {
            "vendor_boost_pct": 0.15,
            "guard_shift": 0.1,
        },
    },
    {
        "festival_id": "LITERARY_EXAMS",
        "name": "Literary Exams",
        "month": 8,
        "day": 1,
        "duration_days": 5,
        "primary_zone": "TEMPLES",
        "theme": "Literary",
        "effects": {
            "vendor_boost_pct": 0.05,
            "guard_shift": 0.08,
            "quest_unlock_tags": ["ScholarTrials"],
        },
    },
    {
        "festival_id": "HARVEST_FAIR",
        "name": "Harvest Fair",
        "month": 8,
        "day": 15,
        "duration_days": 1,
        "primary_zone": "MARKET_EAST",
        "secondary_zones": ["MARKET_WEST"],
        "theme": "Harvest",
        "effects": {
            "vendor_boost_pct": 0.15,
            "crime_shift": 0.08,
            "price_delta_pct": -0.05,
            "guard_shift": 0.05,
        },
    },
)

FACTION_PRESENCE_BLUEPRINTS: Sequence[Tuple[str, str, int]] = (
    ("Court", "CITADEL", 90),
    ("Court", "BARRACKS", 75),
    ("Court", "TEMPLES", 40),
    ("Court", "MARKET_EAST", 35),
    ("Court", "MARKET_WEST", 35),
    ("Court", "WHARF", 30),
    ("Court", "RESIDENTIAL_S", 55),
    ("Merchants", "MARKET_EAST", 70),
    ("Merchants", "MARKET_WEST", 65),
    ("Merchants", "WHARF", 55),
    ("Merchants", "ARTISAN_QTR", 50),
    ("Monastic", "TEMPLES", 80),
    ("Monastic", "RESIDENTIAL_S", 25),
    ("Monastic", "CITADEL", 20),
    ("Rebels", "WHARF", 35),
    ("Rebels", "MARKET_EAST", 25),
    ("Thieves", "WHARF", 30),
    ("Thieves", "MARKET_EAST", 25),
)

HOSTILITY_BLUEPRINTS: Sequence[Tuple[str, str, int]] = (
    ("Court", "Rebels", -70),
    ("Court", "Thieves", -60),
    ("Merchants", "Thieves", -30),
    ("Rebels", "Thieves", 20),
    ("Merchants", "Court", 20),
)

ACCESS_RULE_BLUEPRINTS: Sequence[Dict[str, object]] = (
    {
        "access_rule_id": "COURT_INNER",
        "requires": {
            "story_flags": ["Main_ThangLong_Act1_Cleared"],
            "reputation": [{"faction_id": "Court", "min": 30}],
        },
    },
    {
        "access_rule_id": "ARCHIVE_ONLY",
        "requires": {
            "story_flags": ["ScholarTrials"],
            "reputation": [{"faction_id": "Court", "min": 20}],
        },
    },
    {
        "access_rule_id": "BLACK_MARKET",
        "requires": {
            "reputation": [{"faction_id": "Thieves", "min": 10}],
            "bribe_allowed": True,
        },
    },
)

CRIME_OVERRIDES: Sequence[Tuple[str, bool, bool]] = (
    ("WHARF", True, True),
    ("MARKET_EAST", True, False),
    ("MARKET_WEST", False, False),
)

POI_BLUEPRINTS: Sequence[Dict[str, object]] = (
    {
        "name": "Hoàng thành Thăng Long",
        "district_id": "CITADEL",
        "kind": "district_hub",
        "layers": ["hub", "story", "military"],
        "tags": ["royal", "boss", "approval"],
        "description": "Trung tâm triều đình, nơi hội tụ main arc và boss quốc gia.",
        "owner_faction": "Court",
        "open_hours": ["Dawn", "Day"],
        "capacity": 240,
        "services": ["Ceremony", "Records"],
    },
    {
        "name": "Thư Viện Quốc Sử",
        "district_id": "CITADEL",
        "kind": "archive",
        "layers": ["story", "scholar"],
        "tags": ["records", "quest"],
        "description": "Kho tư liệu của triều đình.",
        "owner_faction": "Court",
        "open_hours": ["Day"],
        "capacity": 80,
        "services": ["Records"],
        "access_rule_id": "ARCHIVE_ONLY",
    },
    {
        "name": "Ngân Khố Đại Việt",
        "district_id": "CITADEL",
        "kind": "treasury",
        "layers": ["economy", "military"],
        "tags": ["treasury", "raid"],
        "description": "Kho bạc quốc gia với bảo vật trấn quốc.",
        "owner_faction": "Court",
        "open_hours": ["Dawn"],
        "capacity": 60,
        "services": ["Ceremony"],
        "access_rule_id": "COURT_INNER",
    },
    {
        "name": "Tháp Canh Đông",
        "district_id": "CITADEL",
        "kind": "guard_tower",
        "layers": ["military"],
        "tags": ["guard"],
        "description": "Tháp canh trấn thủ cửa đông.",
        "owner_faction": "Court",
        "open_hours": ["All"],
        "capacity": 60,
        "services": ["Patrol"],
    },
    {
        "name": "Đồng Xuân Bazaar",
        "district_id": "MARKET_EAST",
        "kind": "market",
        "layers": ["hub", "economy"],
        "tags": ["vendor", "festival"],
        "description": "Trung tâm thương mại lớn nhất Thăng Long.",
        "owner_faction": "Merchants",
        "open_hours": ["Day", "Dusk"],
        "capacity": 600,
        "services": ["Auction", "Repairs"],
    },
    {
        "name": "Đại Sảnh Đấu Giá",
        "district_id": "MARKET_EAST",
        "kind": "auction",
        "layers": ["economy", "story"],
        "tags": ["rare", "quest"],
        "description": "Nơi các thương hội tranh đoạt hàng quý." ,
        "owner_faction": "Merchants",
        "open_hours": ["Day"],
        "capacity": 200,
        "services": ["Auction"],
    },
    {
        "name": "Hội Quán Lồng Đèn",
        "district_id": "MARKET_EAST",
        "kind": "festival_square",
        "layers": ["festival", "story"],
        "tags": ["lantern", "event"],
        "description": "Quảng trường chính của lễ hội Lồng Đèn.",
        "owner_faction": "Merchants",
        "open_hours": ["Dusk", "Night"],
        "capacity": 350,
        "services": ["Performance", "Quest Board"],
    },
    {
        "name": "Phố Nghề Bang Hội",
        "district_id": "MARKET_WEST",
        "kind": "guild_row",
        "layers": ["hub", "craft"],
        "tags": ["guild", "crafting"],
        "description": "Nơi tập trung các phường hội và sạp đặc sản.",
        "owner_faction": "Merchants",
        "open_hours": ["Day"],
        "capacity": 280,
        "services": ["Craft_Tailor", "Craft_Forge"],
    },
    {
        "name": "Lò Rèn Bạch Hổ",
        "district_id": "MARKET_WEST",
        "kind": "forge",
        "layers": ["craft", "martial"],
        "tags": ["weapon", "upgrade"],
        "description": "Xưởng rèn vũ khí cao cấp cho võ lâm.",
        "owner_faction": "Merchants",
        "open_hours": ["Day"],
        "capacity": 120,
        "services": ["Craft_Forge", "Repairs"],
    },
    {
        "name": "Bến Nhị Hà",
        "district_id": "WHARF",
        "kind": "wharf",
        "layers": ["hub", "transport"],
        "tags": ["river", "trade"],
        "description": "Bến chính giao thương đường thủy.",
        "owner_faction": "Merchants",
        "open_hours": ["Dawn", "Day", "Dusk"],
        "capacity": 400,
        "services": ["Transport", "Storage"],
    },
    {
        "name": "Văn Phòng Thuế Quan",
        "district_id": "WHARF",
        "kind": "office",
        "layers": ["economy", "politics"],
        "tags": ["customs", "quest"],
        "description": "Điểm kiểm soát thuế và giấy phép thuyền bè.",
        "owner_faction": "Court",
        "open_hours": ["Day"],
        "capacity": 110,
        "services": ["Contracts"],
    },
    {
        "name": "Lối Vào Chợ Đen",
        "district_id": "WHARF",
        "kind": "blackmarket",
        "layers": ["underground", "economy"],
        "tags": ["smuggling", "rare"],
        "description": "Cửa hầm dẫn tới chợ đen bí mật.",
        "owner_faction": "Thieves",
        "open_hours": ["Night"],
        "capacity": 40,
        "services": ["BlackMarket"],
        "access_rule_id": "BLACK_MARKET",
    },
    {
        "name": "Làng Nghề Bát Tràng",
        "district_id": "ARTISAN_QTR",
        "kind": "craft_hub",
        "layers": ["hub", "craft"],
        "tags": ["ceramic", "daily"],
        "description": "Trung tâm sinh hoạt của thợ gốm.",
        "owner_faction": "Merchants",
        "open_hours": ["Day"],
        "capacity": 220,
        "services": ["Craft_Herbal", "Craft_Forge"],
    },
    {
        "name": "Xưởng Đồng Long",
        "district_id": "ARTISAN_QTR",
        "kind": "foundry",
        "layers": ["craft", "story"],
        "tags": ["bronze", "quest"],
        "description": "Xưởng đúc chuông và vũ khí đồng.",
        "owner_faction": "Merchants",
        "open_hours": ["Day"],
        "capacity": 90,
        "services": ["Craft_Forge"],
    },
    {
        "name": "Doanh Trại Vệ Binh",
        "district_id": "BARRACKS",
        "kind": "barracks",
        "layers": ["hub", "military"],
        "tags": ["training", "quest"],
        "description": "Trung tâm đóng quân của vệ binh hoàng gia.",
        "owner_faction": "Court",
        "open_hours": ["All"],
        "capacity": 260,
        "services": ["Arena", "Training"],
    },
    {
        "name": "Sân Tập Bạch Hổ",
        "district_id": "BARRACKS",
        "kind": "training_ground",
        "layers": ["martial"],
        "tags": ["sparring", "trial"],
        "description": "Sân tập luyện kiếm pháp và võ thuật.",
        "owner_faction": "Court",
        "open_hours": ["Dawn", "Day"],
        "capacity": 150,
        "services": ["Arena"],
    },
    {
        "name": "Văn Miếu",
        "district_id": "TEMPLES",
        "kind": "temple",
        "layers": ["hub", "culture"],
        "tags": ["exam", "ritual"],
        "description": "Nơi tổ chức khoa cử và lễ tế Khổng Tử.",
        "owner_faction": "Monastic",
        "open_hours": ["Day"],
        "capacity": 300,
        "services": ["Exam", "Performance"],
    },
    {
        "name": "Đền Trấn Vũ",
        "district_id": "TEMPLES",
        "kind": "pagoda",
        "layers": ["religion", "story"],
        "tags": ["ritual", "festival"],
        "description": "Ngôi đền linh thiêng bảo hộ kinh thành.",
        "owner_faction": "Monastic",
        "open_hours": ["Dawn", "Day", "Dusk"],
        "capacity": 180,
        "services": ["Ritual"],
    },
    {
        "name": "Phố Bắc Phường",
        "district_id": "RESIDENTIAL_N",
        "kind": "residential",
        "layers": ["hub", "community"],
        "tags": ["commoner", "vendor"],
        "description": "Khu dân cư tấp nập của thường dân.",
        "owner_faction": "Court",
        "open_hours": ["All"],
        "capacity": 240,
        "services": ["Quest Board", "Vendor"],
    },
    {
        "name": "Giếng Đông",
        "district_id": "RESIDENTIAL_N",
        "kind": "well",
        "layers": ["community"],
        "tags": ["water", "gather"],
        "description": "Giếng nước công cộng phục vụ dân cư.",
        "owner_faction": "Court",
        "open_hours": ["All"],
        "capacity": 90,
        "services": ["Vendor"],
    },
    {
        "name": "Trại Gia Viên",
        "district_id": "RESIDENTIAL_S",
        "kind": "noble_estate",
        "layers": ["hub", "noble"],
        "tags": ["noble", "garden"],
        "description": "Khu dinh thự của các đại gia tộc.",
        "owner_faction": "Court",
        "open_hours": ["Day"],
        "capacity": 160,
        "services": ["Social"],
    },
    {
        "name": "Tư Đình Tư Gia",
        "district_id": "RESIDENTIAL_S",
        "kind": "private_shrine",
        "layers": ["religion", "noble"],
        "tags": ["ritual", "secret"],
        "description": "Điện thờ gia tổ của quý tộc.",
        "owner_faction": "Monastic",
        "open_hours": ["Dawn", "Dusk"],
        "capacity": 60,
        "services": ["Ritual"],
    },
)


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


def seed_tuning() -> Tuning:
    save_dataset("tuning", TUNING_DEFAULT.model_dump())
    return TUNING_DEFAULT


def seed_city(tuning: Tuning) -> City:
    population_target = 26000
    city = City(
        city_id="THANG_LONG",
        name="Thăng Long Thành",
        role="CapitalHub",
        level_band=LevelBand(min=20, max=45),
        population_target=population_target,
        food_import_need=population_target * tuning.food_per_capita,
        stability_target=68.0,
        entry_gates=["N", "E", "S", "W"],
        wharves=["To_Lich", "Nhi_Ha"],
    )
    save_dataset("city", city.model_dump())
    return city


def seed_districts(city: City) -> List[District]:
    districts = [District(city_id=city.city_id, **blueprint) for blueprint in DISTRICT_BLUEPRINTS]
    save_dataset("districts", [district.model_dump() for district in districts])
    return districts


def seed_npc_mix() -> List[NPCMix]:
    entries: List[NPCMix] = []
    for district_id, mix in NPC_MIX_TABLE.items():
        total = sum(ratio for _, ratio in mix)
        for archetype, ratio in mix:
            entries.append(NPCMix(district_id=district_id, archetype=archetype, ratio=round(ratio / total, 4)))
    save_dataset("npc_mix", [entry.model_dump() for entry in entries])
    return entries


def seed_trade_network(city: City) -> Tuple[List[TradeNode], List[TradeRoute]]:
    nodes = [TradeNode(node_id=node_id, district_id=district_id, node_type=node_type) for node_id, district_id, node_type in TRADE_NODE_BLUEPRINTS]
    routes = [TradeRoute(**blueprint) for blueprint in TRADE_ROUTE_BLUEPRINTS]
    save_dataset("trade_nodes", [node.model_dump() for node in nodes])
    save_dataset("trade_routes", [route.model_dump() for route in routes])
    return nodes, routes


def seed_festivals() -> List[Festival]:
    festivals = [
        Festival(
            festival_id=spec["festival_id"],
            name=spec["name"],
            month=spec["month"],
            day=spec["day"],
            duration_days=spec["duration_days"],
            primary_zone=spec["primary_zone"],
            secondary_zones=list(spec.get("secondary_zones", [])),
            theme=spec["theme"],
            effects=FestivalEffects(**spec["effects"]),
        )
        for spec in FESTIVAL_BLUEPRINTS
    ]
    save_dataset("festivals", [festival.model_dump() for festival in festivals])
    return festivals


def seed_factions() -> Tuple[List[FactionPresence], List[Hostility]]:
    presence = [
        FactionPresence(faction_id=faction_id, district_id=district_id, influence=influence)
        for faction_id, district_id, influence in FACTION_PRESENCE_BLUEPRINTS
    ]
    hostility = [
        Hostility(faction_a=a, faction_b=b, value=value)
        for a, b, value in HOSTILITY_BLUEPRINTS
    ]
    save_dataset("faction_presence", [entry.model_dump() for entry in presence])
    save_dataset("hostility", [entry.model_dump() for entry in hostility])
    return presence, hostility


def seed_access_rules() -> List[AccessRule]:
    rules = [
        AccessRule(
            access_rule_id=spec["access_rule_id"],
            requires=AccessRequirements(
                story_flags=list(spec.get("requires", {}).get("story_flags", [])),
                reputation=[ReputationGate(**gate) for gate in spec.get("requires", {}).get("reputation", [])],
                attire_tags=list(spec.get("requires", {}).get("attire_tags", [])),
                bribe_allowed=bool(spec.get("requires", {}).get("bribe_allowed", False)),
            ),
        )
        for spec in ACCESS_RULE_BLUEPRINTS
    ]
    save_dataset("access_rules", [rule.model_dump() for rule in rules])
    return rules


def seed_law_and_crime(city: City) -> Tuple[LawCrimeParams, List[DistrictCrimeOverride]]:
    params = LawCrimeParams(
        city_id=city.city_id,
        lawfulness_base=0.68,
        high_crime_threshold=0.3,
        guard_effectiveness=420.0,
    )
    overrides = [
        DistrictCrimeOverride(district_id=district_id, hotspot=hotspot, black_market_flag=black_market)
        for district_id, hotspot, black_market in CRIME_OVERRIDES
    ]
    save_dataset("law_params", params.model_dump())
    save_dataset("district_crime", [override.model_dump() for override in overrides])
    return params, overrides


def generate_poi(
    name: str,
    layers: Iterable[str] | None = None,
    tags: Iterable[str] | None = None,
    *,
    district_id: str,
    coordinates: List[float] | None = None,
    description: str = "",
    kind: str = "landmark",
    media: Iterable[str] | None = None,
    owner_faction: str | None = None,
    open_hours: Iterable[str] | None = None,
    capacity: int = 0,
    services: Iterable[str] | None = None,
    access_rule_id: str | None = None,
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
        media=list(media or []),
        owner_faction_id=owner_faction,
        open_hours=list(open_hours or []),
        capacity=capacity,
        services=list(services or []),
        access_rule_id=access_rule_id,
    )
    poi = POI(id=poi_id, district_id=district_id, geometry=geometry, properties=properties)
    existing = list(load_dataset("pois", factory=list))
    existing.append(poi.model_dump())
    save_dataset("pois", existing)
    return poi


def list_pois() -> List[POI]:
    """Return all stored POIs as models."""

    return [POI.model_validate(item) for item in load_dataset("pois", factory=list)]


def seed_default_pois(seed: int | None = None) -> List[POI]:
    """Populate storage with the default hub templates.

    This is only used for the all-in-one regeneration workflow to provide
    showcase data. Regular generation paths should rely on user-authored POIs
    instead of silently injecting fictional hubs.
    """

    _seed_everything(seed or 42)
    generated: List[POI] = []
    for template in POI_BLUEPRINTS:
        coords = _random_coordinates()
        generated.append(
            generate_poi(
                template["name"],
                layers=template.get("layers"),
                tags=template.get("tags"),
                district_id=str(template["district_id"]),
                coordinates=coords,
                description=str(template.get("description", "")),
                kind=str(template.get("kind", "landmark")),
                media=template.get("media"),
                owner_faction=template.get("owner_faction"),
                open_hours=template.get("open_hours"),
                capacity=int(template.get("capacity", 0)),
                services=template.get("services"),
                access_rule_id=template.get("access_rule_id"),
            )
        )
    return generated


def update_poi(
    poi_id: str,
    *,
    name: str | None = None,
    layers: Iterable[str] | None = None,
    tags: Iterable[str] | None = None,
    description: str | None = None,
    kind: str | None = None,
    media: Iterable[str] | None = None,
    coordinates: List[float] | None = None,
    district_id: str | None = None,
    owner_faction: str | None = None,
    open_hours: Iterable[str] | None = None,
    capacity: int | None = None,
    services: Iterable[str] | None = None,
    access_rule_id: str | None = None,
) -> POI:
    """Update a stored POI and return the refreshed model."""

    pois = list_pois()
    for idx, poi in enumerate(pois):
        if poi.id != poi_id:
            continue
        data = poi.model_dump()
        if name is not None:
            data["properties"]["name"] = name
        if layers is not None:
            data["properties"]["layers"] = list(layers)
        if tags is not None:
            data["properties"]["tags"] = list(tags)
        if description is not None:
            data["properties"]["description"] = description
        if kind is not None:
            data["properties"]["kind"] = kind
        if media is not None:
            data["properties"]["media"] = list(media)
        if coordinates is not None:
            data["geometry"]["coordinates"] = coordinates
        if district_id is not None:
            data["district_id"] = district_id
        if owner_faction is not None:
            data["properties"]["owner_faction_id"] = owner_faction
        if open_hours is not None:
            data["properties"]["open_hours"] = list(open_hours)
        if capacity is not None:
            data["properties"]["capacity"] = capacity
        if services is not None:
            data["properties"]["services"] = list(services)
        if access_rule_id is not None:
            data["properties"]["access_rule_id"] = access_rule_id
        updated = POI.model_validate(data)
        pois[idx] = updated
        save_dataset("pois", [item.model_dump() for item in pois])
        return updated
    raise ValueError(f"POI '{poi_id}' không tồn tại")


def delete_poi(poi_id: str) -> None:
    """Remove a POI from storage."""

    pois = list_pois()
    new_pois = [poi for poi in pois if poi.id != poi_id]
    if len(new_pois) == len(pois):
        raise ValueError(f"POI '{poi_id}' không tồn tại")
    save_dataset("pois", [poi.model_dump() for poi in new_pois])


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

    poi_models = list_pois()
    if poi_pool is not None:
        poi_models = [poi for poi in poi_models if poi.id in poi_pool]
    if not poi_models:
        raise ValueError("Chưa có địa điểm nào để gán hộ dân. Hãy tạo POI trước khi sinh hộ gia đình.")

    districts = [District.model_validate(item) for item in load_dataset("districts", factory=list)]
    npc_mix = [NPCMix.model_validate(item) for item in load_dataset("npc_mix", factory=list)]
    faction_presence = load_dataset("faction_presence", factory=list)

    pois_by_district: Dict[str, List[str]] = defaultdict(list)
    for poi in poi_models:
        pois_by_district[poi.district_id].append(poi.id)

    district_weights: List[Tuple[str, float]] = [
        (district.district_id, max(float(district.population), 1.0)) for district in districts
    ]
    if not district_weights:
        district_weights = [("UNASSIGNED", 1.0)]

    mix_by_district: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    for mix in npc_mix:
        mix_by_district[mix.district_id].append((mix.archetype, max(mix.ratio, 0.01)))

    allegiance_pool = sorted({entry["faction_id"] for entry in faction_presence}) or [
        "Triều đình",
        "Thương hội",
        "Tế đàn",
        "Thủy quân",
        "Nghề thủ công",
        "Văn phái",
    ]

    households: List[Household] = []
    persons: List[Person] = []

    def pick_district() -> str:
        labels, weights = zip(*district_weights)
        return random.choices(labels, weights=weights, k=1)[0]

    for idx in range(count):
        household_id = _household_id(idx + 1)
        district_id = pick_district()
        district_pois = pois_by_district.get(district_id) or [poi.id for poi in poi_models]
        location = HouseholdLocation(poi_id=random.choice(district_pois))
        member_count = random.randint(3, 5)
        members: List[Person] = []
        mix = mix_by_district.get(district_id) or [("Commoner", 1.0)]
        mix_labels, mix_weights = zip(*mix)

        for member_idx in range(member_count):
            sex = random.choice(["M", "F"])
            birth_year = random.randint(1240, 1275)
            profession = random.choices(mix_labels, weights=mix_weights, k=1)[0]
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

        specialty = random.choices(mix_labels, weights=mix_weights, k=1)[0]
        household = Household(
            household_id=household_id,
            house_type=random.choice(["nhà 3 gian", "nhà ống", "nhà mái ngói", "nhà sàn"]),
            status="occupied",
            district=district_id,
            allegiance=random.choice(allegiance_pool),
            specialty=specialty,
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
    save_dataset("city", {})
    save_dataset("districts", [])
    save_dataset("npc_mix", [])
    save_dataset("trade_nodes", [])
    save_dataset("trade_routes", [])
    save_dataset("festivals", [])
    save_dataset("faction_presence", [])
    save_dataset("hostility", [])
    save_dataset("access_rules", [])
    save_dataset("law_params", {})
    save_dataset("district_crime", [])
    save_dataset("tuning", {})

    tuning = seed_tuning()
    city = seed_city(tuning)
    districts = seed_districts(city)
    npc_mix = seed_npc_mix()
    trade_nodes, trade_routes = seed_trade_network(city)
    festivals = seed_festivals()
    faction_presence, hostility = seed_factions()
    access_rules = seed_access_rules()
    law_params, crime_overrides = seed_law_and_crime(city)
    pois = seed_default_pois(seed)
    households = generate_households(len(pois) * 2, seed=seed, poi_pool=[poi.id for poi in pois])
    events = generate_timeline(14, seed=seed)
    quests = generate_quests(6, seed=seed)
    arcs = generate_story_arcs(quests, seed=seed)
    zones = generate_monster_zones(seed=seed)
    features = generate_gameplay_features(seed=seed)
    activities = generate_activities(seed=seed)
    items = generate_items(quests, zones, features, seed=seed)

    return {
        "city": [city.model_dump()],
        "districts": [district.model_dump() for district in districts],
        "npc_mix": [entry.model_dump() for entry in npc_mix],
        "trade_nodes": [node.model_dump() for node in trade_nodes],
        "trade_routes": [route.model_dump() for route in trade_routes],
        "festivals": [festival.model_dump() for festival in festivals],
        "faction_presence": [entry.model_dump() for entry in faction_presence],
        "hostility": [entry.model_dump() for entry in hostility],
        "access_rules": [rule.model_dump() for rule in access_rules],
        "law_params": [law_params.model_dump()],
        "district_crime": [override.model_dump() for override in crime_overrides],
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

