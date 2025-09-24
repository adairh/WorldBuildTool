from fastapi import APIRouter

from ..schemas import WorldBundle, WorldRequest
from ..services import generate_world, summarize_world, validate_world

router = APIRouter(prefix="/world", tags=["world"])


@router.post("/generate", response_model=WorldBundle)
def create_world(request: WorldRequest) -> WorldBundle:
    """Procedurally construct a fully connected world bundle."""

    return generate_world(request)


@router.post("/summary", response_model=dict)
def world_summary(request: WorldRequest) -> dict:
    """Provide a numeric breakdown to guide UI dashboards."""

    bundle = generate_world(request)
    return summarize_world(bundle)


@router.post("/validate", response_model=dict)
def world_validate(request: WorldRequest) -> dict:
    """Generate and validate a bundle, returning errors if any arise."""

    bundle = generate_world(request)
    errors = validate_world(bundle)
    return {"errorCount": len(errors), "errors": errors}
