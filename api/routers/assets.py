from __future__ import annotations

from fastapi import APIRouter

from ..models import Asset
from ..services import add_asset, delete_asset, get_world

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[Asset])
def list_assets() -> list[Asset]:
    return list(get_world().assets)


@router.post("", response_model=Asset)
def create_asset(asset: Asset) -> Asset:
    return add_asset(asset)


@router.put("/{asset_id}", response_model=Asset)
def update_asset(asset_id: str, asset: Asset) -> Asset:
    return add_asset(asset.model_copy(update={"id": asset_id}))


@router.delete("/{asset_id}", status_code=204)
def remove_asset(asset_id: str) -> None:
    delete_asset(asset_id)
