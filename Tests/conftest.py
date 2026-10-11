"""Общие фикстуры тестов."""

import json
from pathlib import Path

import pytest

from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel

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


@pytest.fixture
def units() -> dict[str, MeasurementUnitModel]:
    """Возвращает единицы измерения по умолчанию с ключом по имени."""
    return {unit.name: unit for unit in MeasurementUnitModel.create_default_units()}


@pytest.fixture
def groups() -> dict[str, NomenclatureGroupModel]:
    """Возвращает группы номенклатуры по умолчанию с ключом по имени."""
    return {
        group.name: group for group in NomenclatureGroupModel.create_default_groups()
    }
