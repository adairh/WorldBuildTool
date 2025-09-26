from pathlib import Path

from api.models import Event, Household, Person, POI
from api.services import add_event, add_household, create_or_update_poi, export_world, get_world, world_summary


def test_world_summary_updates_counts(tmp_path) -> None:
    poi = create_or_update_poi(POI(name="Chợ", layer="economy", x=10, y=20))
    household = Household(name="Hộ Trần", home_poi_id=poi.id, members=[Person(name="Trần", birth_year=1260, sex="M")])
    add_household(household)
    add_event(Event(title="Lễ hội", date="1285-03-12", description="", poi_id=poi.id))

    summary = world_summary()
    assert summary["total_pois"] == 1
    assert summary["total_households"] == 1
    assert summary["total_npcs"] == 1
    assert summary["total_events"] == 1
    assert summary["coverage"]["economy"] == 1


def test_export_world_creates_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    from api.config import get_settings

    get_settings.cache_clear()
    get_world(refresh=True)  # initialize storage
    path = export_world()
    assert Path(path).exists()
    content = Path(path).read_text(encoding="utf-8")
    assert "world" not in content  # ensures JSON not zipped but plain
    assert "pois" in content
