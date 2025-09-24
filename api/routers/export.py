from fastapi import APIRouter

from ..services.exporter import export_data

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/")
def export(payload: dict):
    filename = export_data(payload)
    return {"filename": filename}
