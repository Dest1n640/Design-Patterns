"""Общие фикстуры тестов."""

import json
from pathlib import Path

import pytest

from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager

SETTINGS_FILE = Path(__file__).resolve().parents[1] / "settings.json"


@pytest.fixture(autouse=True)
def reset_singletons() -> None:
    """Сбрасывает экземпляры менеджеров, чтобы тесты не зависели друг от друга."""
    SettingsManager._instance = None
    StorageManager._instance = None


@pytest.fixture
def settings_data() -> dict:
    """Возвращает свежую копию содержимого settings.json."""
    return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
