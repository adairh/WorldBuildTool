from fastapi.testclient import TestClient

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_poi_crud_cycle():
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


def test_generation_and_checker():
    household_response = client.post("/households/generate", json={"count": 3, "seed": 10})
    assert household_response.status_code == 200
    households = household_response.json()
    assert len(households) == 3

    events_response = client.post("/events/generate", json={"days": 5, "seed": 10})
    assert events_response.status_code == 200

    checker_response = client.get("/checker/summary")
    assert checker_response.status_code == 200
    assert "issues" in checker_response.json()


def test_export_bundle(tmp_path):
    client.post("/households/generate", json={"count": 2, "seed": 5})
    export_response = client.post("/export", json={"types": ["households", "persons"], "format": "json"})
    assert export_response.status_code == 200
    path = export_response.json()["path"]
    assert path.endswith(".json")
