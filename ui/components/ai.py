from __future__ import annotations

from nicegui import ui

from api.models import PromptRequest
from api.services import ai_memory_summary, prompt_ai


def ai_view() -> None:
    """Render the AI co-pilot panel with prompting and memory overview."""

    channel_input = ui.input("Kênh ghi nhớ", value="workspace").classes("w-full")
    system_box = ui.textarea("System prompt", value="Bạn là nhà thiết kế TL-Forge.").classes("w-full")
    prompt_box = ui.textarea("Prompt", placeholder="Nhập yêu cầu cho ChatGPT...").classes("w-full h-40")
    temperature_slider = ui.slider(min=0.0, max=1.2, value=0.7, step=0.05)
    temperature_slider.props("label='Nhiệt độ' color='orange'")

    output = ui.markdown("*(Chưa có phản hồi)*").classes("w-full bg-slate-900 text-slate-100 p-4 rounded-lg")

    def run_prompt() -> None:
        request = PromptRequest(
            channel=channel_input.value or "workspace",
            prompt=prompt_box.value or "",
            system_prompt=system_box.value or None,
            temperature=float(temperature_slider.value),
        )
        response = prompt_ai(request)
        output.set_content(response or "(Không có phản hồi)")
        populate_memory()

    ui.button("Gửi prompt", on_click=run_prompt).classes("bg-orange-600 text-white")

    memory_table = ui.table(
        columns=[{"name": "channel", "label": "Kênh", "field": "channel"}, {"name": "turns", "label": "Số lượt", "field": "turns"}],
        rows=[],
    ).classes("w-full mt-6")

    def populate_memory() -> None:
        summary = ai_memory_summary()
        memory_table.rows = [
            {"channel": name, "turns": turns}
            for name, turns in sorted(summary.items(), key=lambda item: item[0])
        ]
        memory_table.update()

    populate_memory()
