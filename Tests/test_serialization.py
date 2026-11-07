"""Интеграционные тесты сериализации и десериализации данных хранилища."""

import json

from Src.Core.position_type import PositionType
from Src.Logics.deserialize_factory import DeserializeFactory
from Src.Logics.serialize_factory import SerializeFactory
from Src.Logics.storage_manager import StorageManager
from Src.Models.settings_model import SettingsModel


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
        originals = getattr(manager, collection)
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
        originals = getattr(manager, collection)
        loaded = getattr(restored, collection)
        assert serializer.convert(loaded) == expected
        assert len(loaded) == len(originals)
        for original, model in zip(originals, loaded, strict=True):
            assert type(model) is type(original)
            assert model.id == original.id
            assert model is not original
    assert restored.nomenclature[0].position_type is PositionType.RAW_MATERIAL
