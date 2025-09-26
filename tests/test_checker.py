from api.services import regenerate_foundation, validate_world
from api.storage import load_dataset, save_dataset


def test_validate_world_detects_story_and_feature_gaps() -> None:
    regenerate_foundation(seed=5)

    households = load_dataset("households", factory=list)
    household = households[0]
    bad_hub = household["location"]["poi_id"]
    household["location"]["poi_id"] = None  # force missing hub reference
    save_dataset("households", households)

    features = [item for item in load_dataset("features", factory=list) if item.get("poi_id") != bad_hub]
    save_dataset("features", features)

    zones = [item for item in load_dataset("monster_zones", factory=list) if item.get("anchor_poi_id") != bad_hub]
    save_dataset("monster_zones", zones)

    issues = validate_world()
    assert any("thiếu liên kết hub" in issue for issue in issues)
    assert any("thiếu monster zone" in issue for issue in issues)
    assert any("thiếu tính năng" in issue for issue in issues)


def test_validate_world_trade_and_guard_rules() -> None:
    regenerate_foundation(seed=6)

    save_dataset("trade_routes", [])

    districts = load_dataset("districts", factory=list)
    for district in districts:
        if district.get("district_id") == "MARKET_EAST":
            district["guard_coverage_base"] = 0.0
    save_dataset("districts", districts)

    issues = validate_world()
    assert any("thiếu lương thực" in issue for issue in issues)
    assert any("thiếu lực lượng canh gác" in issue for issue in issues)
