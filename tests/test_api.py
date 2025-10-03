from __future__ import annotations

from fastapi.testclient import TestClient

import api.storage as storage
from api.storage import load_memory


def test_profession_crud(client: TestClient):
    payload = {"name": "Thương nhân", "description": "Buôn bán quanh chợ"}
    resp = client.post("/api/professions/", json=payload)
    assert resp.status_code == 201
    profession = resp.json()

    resp = client.get("/api/professions/")
    assert any(item["name"] == "Thương nhân" for item in resp.json())

    resp = client.put(f"/api/professions/{profession['id']}", json={"id": profession["id"], **payload})
    assert resp.status_code == 200

    resp = client.delete(f"/api/professions/{profession['id']}")
    assert resp.status_code == 204


def test_area_generation_flow(client: TestClient):
    # create profession and area
    prof_resp = client.post("/api/professions/", json={"name": "Nông dân", "description": "Trồng lúa"})
    assert prof_resp.status_code == 201

    area_payload = {
        "name": "Phường Đông",
        "description": "Khu gần chợ",
        "notes": "Tập trung thương nhân",
        "planned_households": 3,
    }
    area_resp = client.post("/api/areas/", json=area_payload)
    area = area_resp.json()

    gen_resp = client.post(f"/api/areas/{area['id']}/generate")
    assert gen_resp.status_code == 200

    households = client.get("/api/state/households").json()
    assert households
    assert all(h["area_id"] == area["id"] for h in households)

    # Export excel should succeed
    export_resp = client.get("/api/export/excel")
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"].startswith("application/vnd.openxmlformats")


def test_memory_loader_handles_concatenated_arrays():
    settings = storage.get_settings()
    payload = """[{\"id\":1}]\n[{\"id\":2}]"""
    settings.memory_file.write_text(payload, encoding="utf-8")

    history = load_memory()
    assert len(history) == 2
    assert history[0]["id"] == 1
    assert history[1]["id"] == 2
