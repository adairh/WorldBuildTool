import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.services import generate_households

client = TestClient(app)


def test_generate_households_requires_pois() -> None:
    with pytest.raises(ValueError):
        generate_households(3, seed=1)


def test_poi_crud_cycle() -> None:
    response = client.post(
        "/pois",
        json={
            "name": "Chợ Tế Xuyên",
            "layers": ["economy", "transport"],
            "tags": ["grain", "textile"],
            "coordinates": [106.25, 21.05],
            "description": "Chợ chính quận Đông",
        },
    )
    assert response.status_code == 200
    poi_id = response.json()["id"]

    list_response = client.get("/pois")
    assert list_response.status_code == 200
    ids = {item["id"] for item in list_response.json()}
    assert poi_id in ids

    update = client.put(
        f"/pois/{poi_id}",
        json={"tags": ["grain", "textile", "salt"]},
    )
    assert update.status_code == 200
    assert "salt" in update.json()["properties"]["tags"]

    delete = client.delete(f"/pois/{poi_id}")
    assert delete.status_code == 204

    confirm = client.get(f"/pois/{poi_id}")
    assert confirm.status_code == 404


def test_world_dashboard_and_story() -> None:
    regenerate = client.post("/world/regenerate", json={"seed": 11})
    assert regenerate.status_code == 200
    assert regenerate.json()["datasets"]["pois"] > 0

    dashboard = client.get("/world/dashboard")
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["story_coverage"] >= 0
    assert "encounter_breakdown" in body

    quests = client.get("/quests")
    assert quests.status_code == 200
    assert len(quests.json()) > 0

    arcs = client.get("/story/arcs")
    assert arcs.status_code == 200
    assert len(arcs.json()) > 0

    zones = client.get("/monsters/zones")
    assert zones.status_code == 200
    assert len(zones.json()) > 0


def test_export_bundle() -> None:
    client.post("/world/regenerate", json={"seed": 7})
    export_response = client.post(
        "/export",
        json={
            "types": ["households", "persons", "quests", "items"],
            "format": "json",
        },
    )
    assert export_response.status_code == 200
    path = export_response.json()["path"]
    assert path.endswith(".json")
