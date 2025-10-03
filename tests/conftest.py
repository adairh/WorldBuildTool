from __future__ import annotations

from pathlib import Path

import pytest

try:
    from fastapi.testclient import TestClient
    from api.config import Settings
    from api.main import app
except ModuleNotFoundError as exc:  # pragma: no cover
    pytest.skip(f"FastAPI not available: {exc}", allow_module_level=True)

from api.storage import load_world, save_world


def _temp_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture(autouse=True)
def override_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    data_dir = _temp_dir(tmp_path)
    state_file = data_dir / "state.json"
    memory_file = data_dir / "memory.json"
    state_file.write_text("{}", encoding="utf-8")
    memory_file.write_text("[]", encoding="utf-8")

    def _settings_factory() -> Settings:
        return Settings(
            data_dir=data_dir,
            state_file=state_file,
            memory_file=memory_file,
            openai_api_key=None,
        )

    monkeypatch.setattr("api.config.get_settings", _settings_factory)
    monkeypatch.setattr("api.services.gpt_client.get_settings", _settings_factory)
    monkeypatch.setattr("api.storage.get_settings", _settings_factory)

    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
