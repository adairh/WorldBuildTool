# TL-Forge (Python-Only Edition)

This repository contains the scaffolding for TL-Forge, a Python-based worldbuilding toolkit
focused on the 13th century Thăng Long setting. It now ships with deep procedural synthesis for
households, martial clans, POIs, timeline events, branching quests, economy telemetry, and narrative
hooks tailored for a Việt Nam wuxia MMORPG sandbox. FastAPI services expose the generators while the
NiceGUI shell gives designers rapid previews.

## Structure

- `api/` – FastAPI application with SQLAlchemy models, routers, and services.
- `ui/` – NiceGUI front-end components.
- `infra/` – Dockerfiles and docker-compose manifest for local development.
- `tests/` – Automated tests for critical services.
- `docs/` – Documentation and style guidance.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn api.main:app --reload
```

Run the UI:

```bash
python -m ui.app
```

## Testing

```bash
pytest
```

## Procedural Worldbuilding Highlights

- **World bundles** – `/world/generate` produces a fully linked dataset (households, persons, POIs,
  events, quests, assets, economy snapshot, and narrative hooks) from a single seed-driven request.
- **Validation** – `/world/validate` reuses the generator and surfaces quest graph and timeline
  inconsistencies to keep your campaign bible coherent.
- **Preview endpoints** – `/households/preview`, `/persons/preview`, `/pois/preview`, `/events/preview`,
  and `/quests/preview` let writers brainstorm focused slices without storing data in the database.
- **Export** – `api.services.exporter.export_world_bundle` packages a manifest plus JSON payloads ready
  for Unity, CSV, or downstream scripting.

### Quick API Session

```python
from api.schemas import WorldRequest
from api.services import generate_world, summarize_world

request = WorldRequest(seed=88, household_count=6, quest_count=4, event_count=10)
bundle = generate_world(request)
print(summarize_world(bundle))
```

### Narrative Possibilities

- River wardens forging pacts with dragon spirits to police illicit qi caravans.
- Political marriage quests between Trần nobles and rebellious martial academies.
- Spirit festival events whose repercussions echo through questlines and assets.

Use the data to drive Unity prototypes, tabletop sessions, or MMO quest pipelines.

## Deployment

Use Docker Compose to start the full stack:

```bash
cd infra
docker-compose up --build
```
