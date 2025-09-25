from __future__ import annotations

from typing import List

from nicegui import ui

from api.models import Item
from api.storage import load_dataset


def _load_items() -> List[Item]:
    return [Item.model_validate(item) for item in load_dataset("items", factory=list)]


def loot_view() -> None:
    """Loot system overview with drop sources."""

    ui.label("Loot Tables").classes("text-2xl font-semibold text-slate-100 mb-2")

    loot_table = ui.table(
        columns=[
            {"name": "item_id", "label": "Item", "field": "item_id"},
            {"name": "name", "label": "Tên", "field": "name"},
            {"name": "rarity", "label": "Độ hiếm", "field": "rarity"},
            {"name": "sources", "label": "Nguồn rơi", "field": "sources"},
        ],
        rows=[],
        row_key="item_id",
    ).classes("w-full shadow-lg")

    def refresh_table() -> None:
        items = _load_items()
        loot_table.rows = [
            {
                "item_id": item.item_id,
                "name": item.name,
                "rarity": item.rarity,
                "sources": ", ".join(f"{src.source_type}:{src.reference_id}" for src in item.sources) or "(chưa có)",
            }
            for item in items
        ]

    refresh_table()

