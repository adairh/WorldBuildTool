import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


def test_root_endpoint():
    from api.main import app

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to TL-Forge API"


def test_world_generation_endpoint():
    from api.main import app

    client = TestClient(app)
    payload = {"seed": 101, "household_count": 4, "quest_count": 3, "event_count": 6}
    response = client.post("/world/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["households"]) == 4
    assert len(data["quests"]) == 3
    assert data["economy"]["totalSilver"] > 0


def test_world_validate_endpoint():
    from api.main import app

    client = TestClient(app)
    payload = {"seed": 202, "household_count": 2, "quest_count": 2, "event_count": 4}
    response = client.post("/world/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "errorCount" in data
    assert isinstance(data["errors"], list)
