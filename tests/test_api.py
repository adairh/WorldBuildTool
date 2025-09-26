import os

os.environ.setdefault("TLFORGE_FAKE_AI", "1")

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_world_default_state() -> None:
    response = client.get("/world")
    assert response.status_code == 200
    body = response.json()
    assert body["pois"] == []
    summary = client.get("/world/summary").json()
    assert summary["total_pois"] == 0


def test_poi_crud_cycle() -> None:
    create = client.post(
        "/pois",
        json={"name": "Chợ Tế Xuyên", "layer": "economy", "x": 120.5, "y": 45.1, "tags": ["market"]},
    )
    assert create.status_code == 200
    poi = create.json()
    poi_id = poi["id"]

    detail = client.get(f"/pois/{poi_id}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Chợ Tế Xuyên"

    updated = client.put(
        f"/pois/{poi_id}",
        json={"id": poi_id, "name": "Chợ mới", "layer": "economy", "x": 10, "y": 20, "tags": []},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Chợ mới"

    delete = client.delete(f"/pois/{poi_id}")
    assert delete.status_code == 204

    missing = client.get(f"/pois/{poi_id}")
    assert missing.status_code == 404


def test_quest_generation_from_prompt() -> None:
    prompt = {
        "prompt": "Giải cứu đoàn thương nhân khỏi bọn cướp trên sông.",
        "steps": 3,
        "seed": 7,
    }
    craft = client.post("/quests/craft", json=prompt)
    assert craft.status_code == 200
    quest = craft.json()
    assert len(quest["steps"]) == 3

    quests = client.get("/quests").json()
    assert any(item["id"] == quest["id"] for item in quests)


def test_household_and_summary_counts() -> None:
    poi = client.post("/pois", json={"name": "Đình", "layer": "culture", "x": 1, "y": 2}).json()
    household_payload = {
        "name": "Gia đình họ Trần",
        "home_poi_id": poi["id"],
        "notes": "",
        "members": [
            {"name": "Trần Văn", "birth_year": 1260, "sex": "M"},
            {"name": "Nguyễn Thị", "birth_year": 1265, "sex": "F"},
        ],
    }
    household = client.post("/households", json=household_payload)
    assert household.status_code == 200

    summary = client.get("/world/summary").json()
    assert summary["total_households"] == 1
    assert summary["total_npcs"] == 2
    assert summary["coverage"]["culture"] == 1


def test_event_crud_cycle() -> None:
    event_payload = {
        "title": "Lễ hội Đèn Lồng",
        "date": "1285-08-15",
        "description": "Lễ hội mùa thu.",
        "poi_id": None,
        "tags": ["festival"],
    }
    created = client.post("/events", json=event_payload)
    assert created.status_code == 200
    event_id = created.json()["id"]

    listed = client.get("/events").json()
    assert any(item["id"] == event_id for item in listed)

    updated = client.put(
        f"/events/{event_id}",
        json={**event_payload, "id": event_id, "description": "Phiên bản mở rộng."},
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "Phiên bản mở rộng."

    remove = client.delete(f"/events/{event_id}")
    assert remove.status_code == 204


def test_ai_prompt_endpoint() -> None:
    payload = {"channel": "test", "prompt": "Tạo một câu giới thiệu."}
    response = client.post("/ai/prompt", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "response" in body and isinstance(body["response"], str)

    memory = client.get("/ai/memory").json()
    assert "test" in memory.get("channels", {})
