from __future__ import annotations

import asyncio
import os
from typing import Any, List

import httpx
from nicegui import ui

API_BASE = os.getenv("TLFORGE_API_BASE", "http://localhost:8000/api")


async def fetch_json(client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Any:
    response = await client.request(method, url, **kwargs)
    response.raise_for_status()
    if response.headers.get("content-type", "").startswith("application/json"):
        return response.json()
    return response


class APIClient:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(base_url=API_BASE)

    async def list_professions(self) -> List[dict]:
        return await fetch_json(self.client, "GET", "/professions/")

    async def save_profession(self, payload: dict, profession_id: str | None = None) -> dict:
        if profession_id:
            return await fetch_json(self.client, "PUT", f"/professions/{profession_id}", json=payload)
        return await fetch_json(self.client, "POST", "/professions/", json=payload)

    async def delete_profession(self, profession_id: str) -> None:
        await fetch_json(self.client, "DELETE", f"/professions/{profession_id}")

    async def list_areas(self) -> List[dict]:
        return await fetch_json(self.client, "GET", "/areas/")

    async def save_area(self, payload: dict, area_id: str | None = None) -> dict:
        if area_id:
            return await fetch_json(self.client, "PUT", f"/areas/{area_id}", json=payload)
        return await fetch_json(self.client, "POST", "/areas/", json=payload)

    async def delete_area(self, area_id: str) -> None:
        await fetch_json(self.client, "DELETE", f"/areas/{area_id}")

    async def generate_area(self, area_id: str) -> dict:
        return await fetch_json(self.client, "POST", f"/areas/{area_id}/generate")

    async def generate_all(self) -> dict:
        return await fetch_json(self.client, "POST", "/areas/generate_all")

    async def state(self) -> dict:
        return await fetch_json(self.client, "GET", "/state/")

    async def delete_household(self, household_id: str) -> None:
        await fetch_json(self.client, "DELETE", f"/state/households/{household_id}")

    async def add_member(self, household_id: str, payload: dict) -> dict:
        return await fetch_json(self.client, "POST", f"/state/households/{household_id}/members", json=payload)

    async def delete_member(self, household_id: str, member_id: str) -> None:
        await fetch_json(self.client, "DELETE", f"/state/households/{household_id}/members/{member_id}")

    async def memory(self) -> List[dict]:
        return await fetch_json(self.client, "GET", "/state/memory")


api_client = APIClient()


def professions_view() -> None:
    table = ui.table(columns=[{"name": "name", "label": "Tên nghề", "field": "name"}, {"name": "description", "label": "Mô tả", "field": "description"}], rows=[], row_key="id").classes("w-full")

    name_input = ui.input("Tên nghề")
    description_input = ui.textarea("Mô tả")

    async def refresh() -> None:
        table.rows = await api_client.list_professions()
        table.update()

    async def create_profession() -> None:
        payload = {"name": name_input.value, "description": description_input.value}
        await api_client.save_profession(payload)
        name_input.value = ""
        description_input.value = ""
        await refresh()

    async def delete_row(event: dict) -> None:
        await api_client.delete_profession(event["row"]["id"])
        await refresh()

    ui.button("Thêm nghề", on_click=lambda: asyncio.create_task(create_profession()))
    table.on("rowContextmenu", lambda e: asyncio.create_task(delete_row(e)))
    ui.timer(0.2, refresh, once=True)


def areas_view() -> None:
    columns = [
        {"name": "name", "label": "Khu vực", "field": "name"},
        {"name": "description", "label": "Mô tả", "field": "description"},
        {"name": "notes", "label": "Ghi chú", "field": "notes"},
        {"name": "planned_households", "label": "Số hộ mục tiêu", "field": "planned_households"},
    ]
    table = ui.table(columns=columns, rows=[], row_key="id").classes("w-full")

    name_input = ui.input("Tên khu")
    description_input = ui.textarea("Mô tả")
    notes_input = ui.textarea("Ghi chú")
    planned_input = ui.number("Số hộ mục tiêu", value=0, format="%.0f")

    async def refresh() -> None:
        table.rows = await api_client.list_areas()
        table.update()

    async def create_area() -> None:
        payload = {
            "name": name_input.value,
            "description": description_input.value,
            "notes": notes_input.value,
            "planned_households": int(planned_input.value or 0),
        }
        await api_client.save_area(payload)
        name_input.value = ""
        description_input.value = ""
        notes_input.value = ""
        planned_input.value = 0
        await refresh()

    async def delete_row(event: dict) -> None:
        await api_client.delete_area(event["row"]["id"])
        await refresh()

    async def generate_row(event: dict) -> None:
        await api_client.generate_area(event["row"]["id"])
        await refresh()

    ui.button("Thêm khu", on_click=lambda: asyncio.create_task(create_area()))
    ui.button("Tạo tất cả", on_click=lambda: asyncio.create_task(api_client.generate_all()))
    table.on("rowClick", lambda e: asyncio.create_task(generate_row(e)))
    table.on("rowContextmenu", lambda e: asyncio.create_task(delete_row(e)))
    ui.timer(0.2, refresh, once=True)


def households_view() -> None:
    table = ui.table(
        columns=[
            {"name": "id", "label": "ID", "field": "id"},
            {"name": "area", "label": "Khu vực", "field": "area"},
            {"name": "profession", "label": "Nghề", "field": "profession"},
            {"name": "people_count", "label": "Số người", "field": "people_count"},
            {"name": "traits", "label": "Đặc điểm", "field": "traits"},
        ],
        rows=[],
        row_key="id",
    ).classes("w-full")

    members_panel = ui.expansion("Thành viên hộ").classes("w-full")

    async def refresh() -> None:
        state = await api_client.state()
        professions = {p["id"]: p["name"] for p in state["professions"]}
        areas = {a["id"]: a["name"] for a in state["areas"]}
        rows = []
        for household in state["households"]:
            rows.append(
                {
                    "id": household["id"],
                    "area": areas.get(household["area_id"], household["area_id"]),
                    "profession": professions.get(household["profession_id"], household["profession_id"]),
                    "people_count": household["people_count"],
                    "traits": ", ".join(household.get("traits", [])),
                    "_raw": household,
                }
            )
        table.rows = rows
        table.update()

    async def show_members(event: dict) -> None:
        data = event["row"].get("_raw")
        if not data:
            return
        members_panel.clear()
        with members_panel:
            ui.label(f"Hộ: {data['id']} - {data.get('notes','')}")
            for member in data.get("members", []):
                with ui.row().classes("items-center gap-2"):
                    ui.label(f"{member['name']} ({member['age']} tuổi, {member['gender']}) - {member['relation']}")
                    ui.button("Xóa", on_click=lambda m=member: asyncio.create_task(api_client.delete_member(data['id'], m['id']))).props("flat")
        members_panel.expand()

    async def delete_household_row(event: dict) -> None:
        await api_client.delete_household(event["row"]["id"])
        await refresh()

    ui.button("Làm mới", on_click=lambda: asyncio.create_task(refresh()))
    ui.button("Tải Excel", on_click=lambda: ui.download(f"{API_BASE}/export/excel"))
    table.on("rowClick", lambda e: asyncio.create_task(show_members(e)))
    table.on("rowContextmenu", lambda e: asyncio.create_task(delete_household_row(e)))
    ui.timer(0.2, refresh, once=True)


def memory_view() -> None:
    log = ui.log(max_lines=200).classes("w-full h-80")

    async def refresh() -> None:
        entries = await api_client.memory()
        log.clear()
        for entry in entries:
            log.push(f"Prompt: {entry.get('prompt','')[:80]} ... | Resp: {entry.get('response','')[:80]}")

    ui.timer(2.0, refresh)


@ui.page("/")
def main_page() -> None:
    with ui.header().classes("items-center justify-between bg-slate-900 text-white"):
        ui.label("TL-Forge Household Planner").classes("text-xl font-semibold")
    with ui.tabs().classes("w-full") as tabs:
        profession_tab = ui.tab("Nghề nghiệp")
        area_tab = ui.tab("Khu vực")
        household_tab = ui.tab("Hộ gia đình")
        memory_tab = ui.tab("ChatGPT Memory")
    with ui.tab_panels(tabs, value=profession_tab).classes("w-full"):
        with ui.tab_panel(profession_tab):
            professions_view()
        with ui.tab_panel(area_tab):
            areas_view()
        with ui.tab_panel(household_tab):
            households_view()
        with ui.tab_panel(memory_tab):
            memory_view()


ui.run(native=False)
