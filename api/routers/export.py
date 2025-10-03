from __future__ import annotations

import io
import zipfile
from xml.sax.saxutils import escape

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
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = "tlforge_households.xlsx"

    def build_sheet_xml(name: str, rows: list[dict]) -> str:
        headers = list(rows[0].keys()) if rows else []

        def cell_xml(value: object) -> str:
            if value is None:
                return "<c/>"
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return f"<c><v>{value}</v></c>"
            text = escape(str(value))
            return f"<c t=\"inlineStr\"><is><t>{text}</t></is></c>"

        def row_xml(index: int, values: list[object]) -> str:
            cells = "".join(cell_xml(v) for v in values)
            return f"<row r=\"{index}\">{cells}</row>"

        lines = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>",
            "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">",
            "<sheetData>",
        ]
        if headers:
            lines.append(row_xml(1, headers))
        for idx, row in enumerate(rows, start=2):
            values = [row.get(header) for header in headers]
            lines.append(row_xml(idx, values))
        lines.append("</sheetData>")
        lines.append("</worksheet>")
        return "".join(lines)

    try:
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            pd.DataFrame(households_rows).to_excel(writer, index=False, sheet_name="Households")
            pd.DataFrame(members_rows).to_excel(writer, index=False, sheet_name="Members")
    except ModuleNotFoundError:
        buffer = io.BytesIO()
        households_xml = build_sheet_xml("Households", households_rows)
        members_xml = build_sheet_xml("Members", members_rows)

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "[Content_Types].xml",
                """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>""".strip(),
            )
            zf.writestr(
                "_rels/.rels",
                """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""".strip(),
            )
            zf.writestr(
                "xl/workbook.xml",
                """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Households" sheetId="1" r:id="rId1"/>
    <sheet name="Members" sheetId="2" r:id="rId2"/>
  </sheets>
</workbook>""".strip(),
            )
            zf.writestr(
                "xl/_rels/workbook.xml.rels",
                """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>""".strip(),
            )
            zf.writestr(
                "xl/styles.xml",
                """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font/></fonts>
  <fills count="1"><fill/></fills>
  <borders count="1"><border/></borders>
  <cellStyleXfs count="1"><xf/></cellStyleXfs>
  <cellXfs count="1"><xf xfId="0" applyNumberFormat="0"/></cellXfs>
</styleSheet>""".strip(),
            )
            zf.writestr("xl/worksheets/sheet1.xml", households_xml)
            zf.writestr("xl/worksheets/sheet2.xml", members_xml)


    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
