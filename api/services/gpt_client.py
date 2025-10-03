from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Iterable, List

try:  # optional dependency, only required when connecting to OpenAI
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - offline fallback
    OpenAI = None  # type: ignore

from ..config import get_settings
from ..models import Area, Household, HouseholdMember, Profession
from ..storage import append_memory


@dataclass
class GPTResponse:
    content: dict
    raw: str
    prompt: str


class GPTClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = None
        if self.settings.openai_api_key and OpenAI is not None:
            self.client = OpenAI(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
            )
        random.seed(42)

    def _record(self, prompt: str, response: str) -> None:
        append_memory({"prompt": prompt, "response": response})

    # -------------------- public API --------------------
    def generate_households(self, area: Area, professions: List[Profession]) -> GPTResponse:
        prompt = self._plan_prompt(area, professions)
        payload = self._call_chatgpt(prompt, response_format="json_object")
        households = payload.get("households") or []
        if not isinstance(households, list):
            households = []
        return GPTResponse(content={"households": households}, raw=json.dumps(payload), prompt=prompt)

    def evaluate_households(self, area: Area, professions: List[Profession], households: List[dict]) -> GPTResponse:
        prompt = self._evaluate_households_prompt(area, professions, households)
        payload = self._call_chatgpt(prompt, response_format="json_object")
        return GPTResponse(content=payload, raw=json.dumps(payload), prompt=prompt)

    def generate_members(self, area: Area, household: dict) -> GPTResponse:
        prompt = self._member_prompt(area, household)
        payload = self._call_chatgpt(prompt, response_format="json_object")
        members = payload.get("members") or []
        return GPTResponse(content={"members": members}, raw=json.dumps(payload), prompt=prompt)

    def evaluate_members(self, area: Area, household: dict, members: List[dict]) -> GPTResponse:
        prompt = self._evaluate_members_prompt(area, household, members)
        payload = self._call_chatgpt(prompt, response_format="json_object")
        return GPTResponse(content=payload, raw=json.dumps(payload), prompt=prompt)

    # -------------------- prompt builders --------------------
    def _plan_prompt(self, area: Area, professions: List[Profession]) -> str:
        profession_text = "\n".join(f"- {p.name}: {p.description}" for p in professions) or "(không có nghề nghiệp nào, hãy tạo phù hợp)"
        return (
            "Bạn là nhà thiết kế cho MMORPG Thăng Long. Dựa trên đặc tả khu vực sau đây, hãy tạo danh sách hộ gia đình.\n"
            f"Khu vực: {area.name}\nMô tả: {area.description}\nGhi chú: {area.notes or 'Không có'}\n"
            f"Số hộ mục tiêu: {area.planned_households}.\n"
            "Danh sách nghề nghiệp được phép:\n"
            f"{profession_text}\n"
            "Hãy trả về JSON với cấu trúc {\"households\": [{\"name\":..., \"profession\":..., \"people_count\":..., \"traits\": [...], \"notes\": ...}]}."
            "Mỗi nghề nên phân bố hợp lý trong khu."
        )

    def _evaluate_households_prompt(self, area: Area, professions: List[Profession], households: List[dict]) -> str:
        return (
            "Đánh giá danh sách hộ sau cho khu vực Thăng Long."
            "Trả lời JSON {\"pass\": bool, \"feedback\": str}. Nếu số hộ không đúng, nghề không hợp lệ, hoặc mô tả nghèo nàn thì fail.\n"
            f"Khu vực: {area.name}. Nghề hợp lệ: {[p.name for p in professions]}.\nDanh sách: {json.dumps(households, ensure_ascii=False)}"
        )

    def _member_prompt(self, area: Area, household: dict) -> str:
        return (
            "Tạo danh sách thành viên cho hộ gia đình Thăng Long."
            "Trả JSON {\"members\":[{\"name\":...,\"age\":...,\"gender\":...,\"relation\":...}]}."
            "Tên kiểu Việt, độ tuổi hợp lý với nghề nghiệp và đặc điểm."
            f"Khu vực: {area.name}. Hộ: {json.dumps(household, ensure_ascii=False)}"
        )

    def _evaluate_members_prompt(self, area: Area, household: dict, members: List[dict]) -> str:
        return (
            "Đánh giá danh sách thành viên."
            "Trả JSON {\"pass\": bool, \"feedback\": str}. Fail nếu tổng người không khớp hoặc quan hệ vô lý."
            f"Khu vực: {area.name}. Hộ: {json.dumps(household, ensure_ascii=False)}. Thành viên: {json.dumps(members, ensure_ascii=False)}"
        )

    # -------------------- call layer --------------------
    def _call_chatgpt(self, prompt: str, response_format: str = "json_object") -> dict:
        if self.client is None:
            return self._offline_stub(prompt)
        response = self.client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": response_format},
        )
        text = response.choices[0].message.content or "{}"
        self._record(prompt, text)
        return json.loads(text)

    # -------------------- offline stub --------------------
    def _offline_stub(self, prompt: str) -> dict:
        # Deterministic pseudo-GPT for offline/testing environments.
        self._record(prompt, "offline_stub")
        if "households" in prompt and "members" not in prompt:
            return self._stub_households(prompt)
        if "members" in prompt and "Đánh giá" not in prompt:
            return self._stub_members(prompt)
        if "Đánh giá" in prompt and "Thành viên" in prompt:
            return {"pass": True, "feedback": "Quan hệ hợp lý"}
        if "Đánh giá" in prompt:
            return {"pass": True, "feedback": "Phân bố nghề hợp lý"}
        return {}

    def _stub_households(self, prompt: str) -> dict:
        # Extract planned households number by simple parsing
        planned = 4
        for token in prompt.split():
            if token.isdigit():
                planned = int(token)
                break
        professions = ["nghề" + str(i) for i in range(1, 5)]
        if "Nghề hợp lệ" in prompt:
            start = prompt.find("[")
            end = prompt.find("]", start)
            if start != -1 and end != -1:
                try:
                    professions = json.loads(prompt[start : end + 1])
                except Exception:
                    pass
        households = []
        for i in range(planned or 1):
            prof_name = professions[i % len(professions)] if professions else f"nghề_{i+1}"
            households.append(
                {
                    "name": f"Gia đình {i+1}",
                    "profession": prof_name,
                    "people_count": 3 + (i % 3),
                    "traits": ["cần cù", "gắn bó cộng đồng" if i % 2 == 0 else "thạo nghề"],
                    "notes": "Sinh hoạt ổn định",
                }
            )
        return {"households": households}

    def _stub_members(self, prompt: str) -> dict:
        base_names = ["Trần", "Lý", "Phạm", "Ngô", "Vũ", "Đinh"]
        genders = ["Nam", "Nữ"]
        members = []
        family_size = 4
        for i in range(family_size):
            members.append(
                {
                    "name": f"{random.choice(base_names)} {random.choice(['Văn','Thị','Hữu','Mỹ'])} {i+1}",
                    "age": random.randint(8, 55),
                    "gender": genders[i % 2],
                    "relation": "Chủ hộ" if i == 0 else "Thành viên",
                }
            )
        return {"members": members}


def build_gpt_client() -> GPTClient:
    return GPTClient()
