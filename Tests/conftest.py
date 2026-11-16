"""Общие фикстуры тестов."""

import json
from enum import Enum
from pathlib import Path

import pytest

from Src.Core.abstract_model import AbstractModel
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel

SETTINGS_FILE = Path(__file__).resolve().parents[1] / "settings.json"


@pytest.fixture(autouse=True)
def reset_singletons(tmp_path, monkeypatch) -> None:
    """Изолирует экземпляры менеджеров и файлы хранилища для каждого теста."""
    SettingsManager._instance = None
    StorageManager._instance = None
    monkeypatch.setattr(StorageManager, "_PROJECT_ROOT", tmp_path)


@pytest.fixture
def register_entity_type(monkeypatch):
    """Подключает тестовую модель одной записью в расширенном перечислении."""
    from Src.Logics import (
        deserialize_factory,
        entity_request_adapter,
        entity_service,
        entity_type,
        storage_manager,
    )

    def register(collection_name: str, model_type: type[AbstractModel]) -> None:
        """Добавляет модель в перечисление всех потребителей на время теста."""
        members = {item.name: item.value for item in entity_type.EntityType}
        members[collection_name.upper()] = model_type
        extended = Enum("EntityType", members)
        for module in (
            entity_type,
            deserialize_factory,
            entity_request_adapter,
            entity_service,
            storage_manager,
        ):
            monkeypatch.setattr(module, "EntityType", extended)

    return register


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
