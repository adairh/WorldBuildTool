import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

pytest.importorskip("pydantic")

from api.config import get_settings
from api.storage import ensure_storage_dir, reset_storage


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    get_settings.cache_clear()
    ensure_storage_dir()
    reset_storage()
    yield
    get_settings.cache_clear()
