from __future__ import annotations

import json
from itertools import cycle
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ..config import ensure_storage_dir, get_settings
from ..models import Asset, Event, Household, POI, PromptRequest, StoryPrompt

try:  # pragma: no cover - optional dependency
    import openai  # type: ignore
except Exception:  # pragma: no cover
    openai = None


class ChatGPTUnavailable(RuntimeError):
    """Raised when no OpenAI client is available and no fallback was provided."""


class ChatGPTClient:
    """Shared helper that wraps ChatGPT access and manages local memory."""

    def __init__(self) -> None:
        self.settings = get_settings()
        ensure_storage_dir()
        self.memory_path: Path = self.settings.storage_dir / self.settings.memory_filename
        self.memory: Dict[str, List[Dict[str, str]]] = self._load_memory()
        self.max_history = max(2, self.settings.max_memory_messages)
        self._available = self._init_openai()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _init_openai(self) -> bool:
        if self.settings.use_fake_ai:
            return False
        if openai is None:
            return False
        if not self.settings.openai_api_key:
            return False
        openai.api_key = self.settings.openai_api_key
        return True

    def _load_memory(self) -> Dict[str, List[Dict[str, str]]]:
        if not self.memory_path.exists():
            return {}
        try:
            payload = json.loads(self.memory_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return {channel: list(entries) for channel, entries in payload.items() if isinstance(entries, list)}
        except json.JSONDecodeError:
            pass
        return {}

    def _save_memory(self) -> None:
        self.memory_path.write_text(json.dumps(self.memory, ensure_ascii=False, indent=2), encoding="utf-8")

    def _history(self, channel: str) -> List[Dict[str, str]]:
        return self.memory.setdefault(channel, [])

    def _respond(
        self,
        channel: str,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: Optional[float] = None,
        fallback: Optional[Callable[[str], str]] = None,
    ) -> str:
        history = self._history(channel)
        history_slice = history[-self.max_history :]
        messages = [{"role": item["role"], "content": item["content"]} for item in history_slice]
        messages.insert(0, {"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        if self._available:
            completion = openai.ChatCompletion.create(  # type: ignore[attr-defined]
                model=self.settings.openai_model,
                messages=messages,
                temperature=temperature if temperature is not None else self.settings.openai_temperature,
            )
            content = str(completion.choices[0].message["content"]).strip()  # type: ignore[index]
        else:
            if not fallback:
                raise ChatGPTUnavailable(
                    "OpenAI API is unavailable. Provide OPENAI_API_KEY or enable fake AI mode via TLFORGE_FAKE_AI=1."
                )
            content = fallback(user_prompt)

        history.append({"role": "user", "content": user_prompt})
        history.append({"role": "assistant", "content": content})
        self._save_memory()
        return content

    def _respond_json(
        self,
        channel: str,
        system_prompt: str,
        user_prompt: str,
        *,
        fallback: Dict[str, object],
    ) -> Dict[str, object]:
        payload = self._respond(
            channel,
            system_prompt,
            user_prompt,
            fallback=lambda _prompt: json.dumps(fallback, ensure_ascii=False),
        )
        try:
            data = json.loads(payload)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return fallback

    # ------------------------------------------------------------------
    # Public API helpers
    # ------------------------------------------------------------------
    def prompt(self, request: PromptRequest) -> str:
        """Execute a free-form prompt and store its memory."""

        system_prompt = request.system_prompt or (
            "Bạn là nhà thiết kế game AAA cho TL-Forge, luôn trả lời bằng tiếng Việt trang trọng."
        )
        return self._respond(
            request.channel or "workspace",
            system_prompt,
            request.prompt,
            temperature=request.temperature,
            fallback=lambda _: self._fallback_generic(request.prompt),
        )

    def memory_summary(self) -> Dict[str, int]:
        """Return the number of turns stored per channel."""

        return {channel: len(entries) for channel, entries in self.memory.items()}

    def channel_history(self, channel: str) -> List[Dict[str, str]]:
        return list(self.memory.get(channel, []))

    def clear_channel(self, channel: str) -> None:
        if channel in self.memory:
            del self.memory[channel]
            self._save_memory()

    # ------------------------------------------------------------------
    # Domain-specific helpers used across the toolkit
    # ------------------------------------------------------------------
    def describe_poi(self, poi: POI) -> str:
        tags = ", ".join(poi.tags) if poi.tags else poi.layer
        prompt = (
            "Mô tả địa điểm trong Thăng Long thời Trần với tối đa 2 câu. "
            "Nêu rõ chức năng và bầu không khí, chú ý các thẻ sau: {tags}."
        ).format(tags=tags)
        return self._respond(
            "poi",
            "Bạn là nhà biên kịch thế giới Thăng Long, luôn viết giàu hình ảnh nhưng súc tích.",
            f"Tên địa điểm: {poi.name}. Layer: {poi.layer}. Tọa độ: ({poi.x:.1f}, {poi.y:.1f}). {prompt}",
            fallback=lambda _: self._fallback_poi_description(poi),
        )

    def suggest_poi_tags(self, poi: POI) -> List[str]:
        fallback = self._fallback_poi_tags(poi)
        data = self._respond_json(
            "poi-tags",
            "Bạn gợi ý metadata cho MMORPG Việt Nam.",
            (
                "Trả về JSON với khóa 'tags' (mảng tag chữ thường) cho địa điểm: {name}. "
                "Layer: {layer}. Tags hiện có: {tags}."
            ).format(name=poi.name, layer=poi.layer, tags=", ".join(poi.tags)),
            fallback={"tags": fallback},
        )
        tags = data.get("tags", fallback)
        return [str(tag) for tag in tags if isinstance(tag, str)] or fallback

    def enrich_household_notes(self, household: Household) -> str:
        members = ", ".join(f"{member.name} ({member.sex})" for member in household.members)
        return self._respond(
            "household",
            "Bạn tóm tắt quan hệ gia đình trong Thăng Long bằng giọng kể lịch sử.",
            f"Gia đình: {household.name}. Thành viên: {members}. Yêu cầu viết 2 câu giới thiệu.",
            fallback=lambda _: self._fallback_household_notes(household),
        )

    def suggest_professions(self, household: Household) -> Dict[str, str]:
        fallback = self._fallback_professions(household)
        data = self._respond_json(
            "professions",
            "Bạn gán nghề nghiệp phù hợp theo bối cảnh thế kỷ 13.",
            (
                "Trả về JSON với khóa 'professions' là object map từ household_member_id sang nghề nghiệp. "
                "Household: {name}. Các thành viên (id:name:nghề hiện tại hoặc null): {members}."
            ).format(
                name=household.name,
                members=", ".join(
                    f"{member.id}:{member.name}:{member.profession or 'null'}" for member in household.members
                ),
            ),
            fallback={"professions": fallback},
        )
        professions = data.get("professions", fallback)
        result: Dict[str, str] = {}
        if isinstance(professions, dict):
            for member in household.members:
                value = professions.get(member.id) or professions.get(member.name)
                if isinstance(value, str) and value.strip():
                    result[member.id] = value.strip()
        if not result:
            result = fallback
        return result

    def describe_event(self, event: Event) -> str:
        return self._respond(
            "events",
            "Bạn là người kể sử thành Thăng Long.",
            (
                "Viết đoạn mô tả ngắn (tối đa 2 câu) cho sự kiện '{title}' diễn ra ngày {date}. "
                "Thẻ: {tags}."
            ).format(title=event.title, date=event.date, tags=", ".join(event.tags or [])),
            fallback=lambda _: self._fallback_event(event),
        )

    def annotate_asset(self, asset: Asset) -> str:
        return self._respond(
            "assets",
            "Bạn là giám đốc nghệ thuật AAA, viết ghi chú súc tích.",
            (
                "Asset: {name}. Loại: {kind}. Tags: {tags}. Viết 1-2 câu mô tả ý đồ art cho TL-Forge."
            ).format(name=asset.name, kind=asset.kind, tags=", ".join(asset.tags or [])),
            fallback=lambda _: self._fallback_asset(asset),
        )

    def quest_beats(self, prompt: StoryPrompt) -> List[str]:
        fallback_steps = self._fallback_quest_steps(prompt)
        data = self._respond_json(
            "quests",
            "Bạn là nhà thiết kế quest MMORPG.",
            (
                "Tạo JSON {{\"steps\": [..]}} với {count} bước cho cốt truyện: {prompt}. "
                "Mỗi bước 1 câu hành động, bối cảnh Thăng Long, giọng wuxia.".format(
                    count=prompt.steps, prompt=prompt.prompt
                ),
            ),
            fallback={"steps": fallback_steps},
        )
        steps = data.get("steps", fallback_steps)
        if isinstance(steps, list):
            cleaned = [str(item).strip() for item in steps if str(item).strip()]
            if cleaned:
                return cleaned[: prompt.steps]
        return fallback_steps

    # ------------------------------------------------------------------
    # Fallback helpers (deterministic for tests / offline use)
    # ------------------------------------------------------------------
    def _fallback_generic(self, prompt: str) -> str:
        return f"[Offline AI] {prompt.strip()}" if prompt.strip() else "[Offline AI] Đang chờ nội dung."

    def _fallback_poi_description(self, poi: POI) -> str:
        tag_text = ", ".join(poi.tags) if poi.tags else poi.layer
        return f"{poi.name} thuộc khu {poi.layer}, nổi bật với các yếu tố: {tag_text}."

    def _fallback_poi_tags(self, poi: POI) -> List[str]:
        base: List[str] = []
        if poi.layer:
            base.append(poi.layer.lower())
        base.extend(tag.lower() for tag in poi.tags)
        return sorted(set(base)) or ["general"]

    def _fallback_household_notes(self, household: Household) -> str:
        members = ", ".join(member.name for member in household.members) or "chưa ghi nhận thành viên"
        return f"Gia đình {household.name} cư trú tại {household.home_poi_id or 'Thăng Long'}, gồm {members}."

    def _fallback_professions(self, household: Household) -> Dict[str, str]:
        defaults = cycle(["thương nhân", "thợ thủ công", "quan lại", "võ sĩ", "thủy thủ", "nông dân"])
        mapping: Dict[str, str] = {}
        for member in household.members:
            if member.profession:
                mapping[member.id] = member.profession
            else:
                mapping[member.id] = next(defaults)
        return mapping

    def _fallback_event(self, event: Event) -> str:
        return f"Sự kiện '{event.title}' diễn ra ngày {event.date}, mang sắc thái {'/'.join(event.tags or ['địa phương'])}."

    def _fallback_asset(self, asset: Asset) -> str:
        return f"Asset {asset.name} ({asset.kind}) đang ở trạng thái {asset.status}."

    def _fallback_quest_steps(self, prompt: StoryPrompt) -> List[str]:
        seed = prompt.seed if prompt.seed is not None else sum(map(ord, prompt.prompt))
        verbs = ["Điều tra", "Đàm phán", "Bảo vệ", "Khám phá", "Trấn áp", "Đàm luận"]
        nouns = ["bí ẩn", "liên minh", "buổi lễ", "hành trình", "âm mưu", "di tích"]
        random_index = seed % len(verbs) if verbs else 0
        return [
            f"{verbs[(random_index + i) % len(verbs)]} {nouns[(random_index + i) % len(nouns)]} tại Thăng Long"
            for i in range(prompt.steps)
        ]


_client: Optional[ChatGPTClient] = None


def get_chatgpt() -> ChatGPTClient:
    global _client
    if _client is None:
        _client = ChatGPTClient()
    return _client


def prompt_ai(request: PromptRequest) -> str:
    return get_chatgpt().prompt(request)


def ai_memory_summary() -> Dict[str, int]:
    return get_chatgpt().memory_summary()


def ai_channel_history(channel: str) -> List[Dict[str, str]]:
    return get_chatgpt().channel_history(channel)


def clear_ai_channel(channel: str) -> None:
    get_chatgpt().clear_channel(channel)
