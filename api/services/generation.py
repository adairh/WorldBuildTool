from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Tuple

from ..config import get_settings
from ..models import Area, Household, HouseholdMember, Profession, WorldState
from ..storage import save_world
from .gpt_client import GPTClient

_executor = ThreadPoolExecutor(max_workers=8)


class GenerationError(RuntimeError):
    pass


def generate_households_for_areas(state: WorldState, area_ids: Iterable[str], gpt: GPTClient | None = None) -> Tuple[WorldState, Dict[str, str]]:
    gpt_client = gpt or GPTClient()
    areas = [state.find_area(aid) for aid in area_ids]
    professions = state.professions
    results: Dict[str, str] = {}
    futures = {
        _executor.submit(_generate_for_area, area, professions, gpt_client): area.id for area in areas
    }

    new_households: List[Household] = [h for h in state.households if h.area_id not in {a.id for a in areas}]

    for future in as_completed(futures):
        area_id = futures[future]
        try:
            households = future.result()
            new_households.extend(households)
            results[area_id] = "success"
        except Exception as exc:  # pragma: no cover
            results[area_id] = str(exc)

    state.households = new_households
    save_world(state)
    return state, results


def _generate_for_area(
    area: Area,
    professions: List[Profession],
    gpt_client: GPTClient,
) -> List[Household]:
    settings = get_settings()
    retries = settings.generation_max_retries
    households: List[dict] = []
    feedback = ""

    if area.planned_households <= 0:
        return []

    while retries > 0:
        plan_response = gpt_client.generate_households(area, professions)
        households = plan_response.content.get("households", [])
        eval_response = gpt_client.evaluate_households(area, professions, households)
        if eval_response.content.get("pass", True):
            feedback = eval_response.content.get("feedback", "")
            break
        retries -= 1
    else:
        raise GenerationError(f"Không thể tạo hộ gia đình hợp lệ cho khu {area.name}")

    results: List[Household] = []
    for raw_household in households:
        member_retries = settings.generation_max_retries
        members: List[dict] = []
        member_feedback = ""
        while member_retries > 0:
            member_response = gpt_client.generate_members(area, raw_household)
            members = member_response.content.get("members", [])
            eval_member = gpt_client.evaluate_members(area, raw_household, members)
            if eval_member.content.get("pass", True):
                member_feedback = eval_member.content.get("feedback", "")
                break
            member_retries -= 1
        else:
            raise GenerationError(f"Không thể tạo thành viên hợp lệ cho hộ {raw_household.get('name')}")

        profession_id = _resolve_profession_id(raw_household.get("profession"), professions)
        household = Household(
            area_id=area.id,
            profession_id=profession_id,
            people_count=int(raw_household.get("people_count", len(members) or 1)),
            traits=list(raw_household.get("traits", [])),
            notes=str(raw_household.get("notes", "")),
            evaluation_feedback="; ".join(filter(None, [feedback, member_feedback])) or None,
        )
        household.members = [
            HouseholdMember(
                name=m.get("name", ""),
                age=int(m.get("age", 0)),
                gender=str(m.get("gender", "")),
                relation=str(m.get("relation", "")),
            )
            for m in members
        ]
        household.people_count = max(household.people_count, len(household.members) or 1)
        results.append(household)

    return results


def _resolve_profession_id(profession_name: str | None, professions: List[Profession]) -> str:
    if not professions:
        return Profession(name=profession_name or "Tự do").id
    for prof in professions:
        if prof.name.lower() == (profession_name or "").lower():
            return prof.id
    return professions[0].id
