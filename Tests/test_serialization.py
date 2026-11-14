"""Интеграционные тесты сериализации и десериализации данных хранилища."""

import json

import pytest

from Src.Core.exception import ValidationException
from Src.Core.position_type import PositionType
from Src.Logics.deserialize_factory import DeserializeFactory
from Src.Logics.serialize_factory import SerializeFactory
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager
from Src.Models.settings_model import SettingsModel


def test_serialization__settings_json__all_fields_restored():
    """Общая фабрика восстанавливает свойства настроек, организацию и перечисление."""
    # Подготовка
    manager = SettingsManager()
    manager.read()
    original = manager.settings
    serializer = SerializeFactory()
    data = json.loads(json.dumps(serializer.convert(original)))

    # Действия
    restored = DeserializeFactory().convert(data)

    # Проверки
    assert type(restored) is SettingsModel
    assert restored is not original
    assert restored.organization is not original.organization
    assert restored.response_format is original.response_format
    assert serializer.convert(restored) == data


def test_serialization__storage_json__all_model_fields_restored(tmp_path):
    """Все справочники из JSON совпадают с исходными моделями хранилища по полям."""
    # Подготовка
    manager = StorageManager()
    settings = SettingsModel()
    settings.first_start = True
    manager.start(settings)
    file_name = tmp_path / "storage.json"
    manager.save(str(file_name))
    data = json.loads(file_name.read_text(encoding="utf-8"))

    # Действия
    restored = DeserializeFactory().convert(data)

    # Проверки
    serializer = SerializeFactory()
    for collection, models in restored.items():
        originals = manager.get_entities(collection)
        assert len(models) == len(originals)
        for original, loaded in zip(originals, models, strict=True):
            assert type(loaded) is type(original)
            assert loaded is not original
            assert serializer.convert(loaded) == serializer.convert(original)
    assert restored["nomenclature"][0].position_type is PositionType.RAW_MATERIAL
    dough = restored["technological_maps"][0].dishes[1].ingredients[0]
    assert dough.ingredients[0].position_type is PositionType.RAW_MATERIAL


def test_serialization__manager_read__saved_models_restored(tmp_path):
    """Менеджер загружает сохранённые поля и id вместо формирования новых моделей."""
    # Подготовка
    manager = StorageManager()
    settings = SettingsModel()
    settings.first_start = True
    manager.start(settings)
    file_name = tmp_path / "storage.json"
    manager.save(str(file_name))
    data = json.loads(file_name.read_text(encoding="utf-8"))
    data["nomenclature"][0]["full_name"] = "Название из сохранённого файла"
    file_name.write_text(json.dumps(data), encoding="utf-8")
    StorageManager._instance = None
    restored = StorageManager()

    # Действия
    restored.read(str(file_name))

    # Проверки
    assert restored.is_loaded
    serializer = SerializeFactory()
    for collection, expected in data.items():
        originals = manager.get_entities(collection)
        loaded = restored.get_entities(collection)
        assert serializer.convert(loaded) == expected
        assert len(loaded) == len(originals)
        for original, model in zip(originals, loaded, strict=True):
            assert type(model) is type(original)
            assert model.id == original.id
            assert model is not original
    assert restored.nomenclature[0].position_type is PositionType.RAW_MATERIAL


def test_serialization__legacy_snapshot__nested_models_indexed_and_shared(tmp_path):
    """Старый JSON заполняет новые коллекции и восстанавливает общие ссылки."""
    # Подготовка
    manager = StorageManager()
    settings = SettingsModel()
    settings.first_start = True
    manager.start(settings)
    file_name = tmp_path / "storage.json"
    manager.save(str(file_name))
    data = json.loads(file_name.read_text(encoding="utf-8"))
    for collection in ("organizations", "premises", "dishes", "ingredients"):
        del data[collection]
    data["measurement_units"].reverse()
    pizza = data["technological_maps"][0]["dishes"][1]
    data["technological_maps"][0]["dishes"] = [pizza]
    file_name.write_text(json.dumps(data), encoding="utf-8")
    StorageManager._instance = None
    restored = StorageManager()

    # Действия
    restored.read(str(file_name))
    loaded_pizza = restored.technological_maps[0].dishes[0]
    dough = loaded_pizza.ingredients[0]
    units = {unit.name: unit for unit in restored.measurement_units}
    owners = {
        owner.id: owner for owner in [*restored.restaurants, *restored.production_shops]
    }

    # Проверки
    assert units["килограмм"].base_unit is units["грамм"]
    assert [unit.id for unit in restored.measurement_units] == [
        unit["id"] for unit in data["measurement_units"]
    ]
    assert len(restored.get_entities("premises")) == 3
    assert len(restored.get_entities("dishes")) == 2
    assert len(restored.get_entities("ingredients")) == 9
    assert loaded_pizza is restored.get_entity("dishes", loaded_pizza.id)
    assert dough is restored.get_entity("dishes", dough.id)
    ingredient = dough.ingredients[0]
    assert ingredient is restored.get_entity("ingredients", ingredient.id)
    assert ingredient.measurement_unit is units["грамм"]
    for position in restored.nomenclature:
        assert position.group is restored.get_entity(
            "nomenclature_groups", position.group.id
        )
        assert position.measurement_unit is restored.get_entity(
            "measurement_units", position.measurement_unit.id
        )
    for warehouse in restored.warehouses:
        assert warehouse.premises is restored.get_entity(
            "premises", warehouse.premises.id
        )
        assert warehouse.warehouse_owner is owners[warehouse.warehouse_owner.id]


def test_serialization__conflicting_nested_model__previous_graph_kept(tmp_path):
    """Конфликт вложенных данных не заменяет ни одну коллекцию хранилища."""
    # Подготовка
    manager = StorageManager()
    settings = SettingsModel()
    settings.first_start = True
    manager.start(settings)
    originals = {
        name: manager.get_entities(name) for name in manager.get_entity_types()
    }
    file_name = tmp_path / "storage.json"
    manager.save(str(file_name))
    data = json.loads(file_name.read_text(encoding="utf-8"))
    data["nomenclature"][0]["group"]["name"] = "Конфликтующее название"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.read(str(file_name))

    # Проверки
    assert exc_info.value.field == "id"
    assert manager.is_loaded
    for name, original in originals.items():
        loaded = manager.get_entities(name)
        assert len(loaded) == len(original)
        assert all(
            first is second for first, second in zip(loaded, original, strict=True)
        )
