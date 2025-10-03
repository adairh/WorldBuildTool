from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..storage import load_world

router = APIRouter()


@router.get("/excel")
def export_excel() -> StreamingResponse:
    state = load_world()
    households_rows = []
    members_rows = []
    profession_lookup = {p.id: p.name for p in state.professions}
    area_lookup = {a.id: a.name for a in state.areas}

    for household in state.households:
        households_rows.append(
            {
                "household_id": household.id,
                "area": area_lookup.get(household.area_id, household.area_id),
                "profession": profession_lookup.get(household.profession_id, household.profession_id),
                "people_count": household.people_count,
                "traits": ", ".join(household.traits),
                "notes": household.notes,
                "evaluation_feedback": household.evaluation_feedback or "",
            }
        )
        for member in household.members:
            members_rows.append(
                {
                    "household_id": household.id,
                    "name": member.name,
                    "age": member.age,
                    "gender": member.gender,
                    "relation": member.relation,
                }
            )

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame(households_rows).to_excel(writer, index=False, sheet_name="Households")
        pd.DataFrame(members_rows).to_excel(writer, index=False, sheet_name="Members")
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=tlforge_households.xlsx"},
    )
