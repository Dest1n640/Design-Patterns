"""Интеграционные тесты автосохранения и восстановления JSON-хранилища."""

import json
from functools import partial
from unittest.mock import Mock

import pytest

from Src.Core.exception import (
    ApplicationException,
    ConflictException,
    NotFoundException,
    PersistenceException,
    ValidationException,
)
from Src.Logics.entity_service import EntityService
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.settings_model import SettingsModel


@pytest.fixture
def persistent_storage(tmp_path):
    """Создаёт пустое хранилище с отдельным файлом автосохранения."""
    manager = StorageManager()
    file_name = tmp_path / "storage.json"
    manager.start(SettingsModel(), str(file_name))
    return manager, file_name


def _restart(file_name) -> StorageManager:
    """Создаёт новый менеджер с first_start=True для проверки приоритета файла."""
    StorageManager._instance = None
    settings = SettingsModel()
    settings.first_start = True
    manager = StorageManager()
    manager.start(settings, str(file_name))
    return manager


def test_storage_persistence__crud_and_restarts__changes_restored(persistent_storage):
    """Создание, изменение и удаление восстанавливаются после каждого перезапуска."""
    # Подготовка
    manager, file_name = persistent_storage

    # Действия
    created = EntityService(manager).create(NomenclatureGroupModel.create("Группа"))
    after_creation = _restart(file_name)
    initial_name = after_creation.get_entity("nomenclature_groups", created.id).name
    replacement = NomenclatureGroupModel.create("Новое название")
    replacement.id = created.id
    EntityService(after_creation).update("nomenclature_groups", created.id, replacement)
    after_update = _restart(file_name)
    updated_name = after_update.get_entity("nomenclature_groups", created.id).name
    EntityService(after_update).delete("nomenclature_groups", created.id)
    after_deletion = _restart(file_name)

    # Проверки
    assert initial_name == "Группа"
    assert updated_name == "Новое название"
    assert after_deletion.nomenclature_groups == []
    assert after_deletion.nomenclature == []
    assert (
        json.loads(file_name.read_text(encoding="utf-8"))["nomenclature_groups"] == []
    )


def test_storage_persistence__unknown_collection__original_file_kept(tmp_path):
    """Запуск отклоняет неизвестную коллекцию до перезаписи файла."""
    # Подготовка
    settings = SettingsManager()
    settings.read()
    file_name = tmp_path / "storage.json"
    original_file = b'{"measurement_units": [], "future_collection": [{"id": "a"}]}'
    file_name.write_bytes(original_file)
    manager = StorageManager()

    # Действия
    with pytest.raises(ValidationException, match="future_collection"):
        manager.start(settings.settings, str(file_name))

    # Проверки
    assert file_name.read_bytes() == original_file
    assert not manager.is_loaded


@pytest.mark.parametrize("operation", ["create", "update", "delete"])
def test_storage_persistence__replace_failure__file_and_graph_kept(
    persistent_storage, monkeypatch, operation
):
    """Ошибка замены файла откатывает CRUD и сохраняет все общие ссылки."""
    # Подготовка
    manager, file_name = persistent_storage
    service = EntityService(manager)
    gram = service.create(MeasurementUnitModel.create_gram())
    kilogram = service.create(MeasurementUnitModel.create_kilogram(gram))
    group = service.create(NomenclatureGroupModel.create("Группа"))
    replacement = gram.clone()
    replacement.name = "Новое имя"
    original_file = file_name.read_bytes()
    operations = {
        "create": partial(service.create, NomenclatureGroupModel.create("Новая")),
        "update": partial(service.update, "measurement_units", gram.id, replacement),
        "delete": partial(service.delete, "nomenclature_groups", group.id),
    }

    def fail_replace(source, target) -> None:
        """Имитирует отказ диска при атомарной замене файла."""
        raise OSError("Запись недоступна")

    monkeypatch.setattr("Src.Logics.storage_manager.os.replace", fail_replace)

    # Действия
    with pytest.raises(PersistenceException):
        operations[operation]()

    # Проверки
    assert file_name.read_bytes() == original_file
    assert manager.nomenclature_groups == [group]
    assert manager.get_entity("measurement_units", gram.id) is gram
    assert gram.name == "грамм"
    assert kilogram.base_unit is gram
    assert manager.get_reference_count(gram.id) == 1
    assert manager.get_reference_count(kilogram.id) == 0
    assert manager.get_reference_count(group.id) == 0
    assert sorted(path.name for path in file_name.parent.iterdir()) == ["storage.json"]


def test_storage_persistence__partial_write_failure__old_file_kept(
    persistent_storage, monkeypatch
):
    """Незавершённая запись временного файла сохраняет предыдущий снимок."""
    # Подготовка
    manager, file_name = persistent_storage
    original_file = file_name.read_bytes()

    def fail_dump(data, file, **kwargs) -> None:
        """Обрывает запись после появления части данных во временном файле."""
        file.write('{"partial":')
        raise OSError("Ошибка записи")

    monkeypatch.setattr("Src.Logics.storage_manager.json.dump", fail_dump)

    # Действия
    with pytest.raises(PersistenceException):
        EntityService(manager).create(NomenclatureGroupModel.create("Группа"))

    # Проверки
    assert file_name.read_bytes() == original_file
    assert manager.nomenclature_groups == []
    assert sorted(path.name for path in file_name.parent.iterdir()) == ["storage.json"]


def test_storage_persistence__failed_link_change__reference_counts_kept(
    persistent_storage, monkeypatch
):
    """Ошибка записи новой связи сохраняет прежние счётчики и экземпляры."""
    # Подготовка
    manager, file_name = persistent_storage
    service = EntityService(manager)
    kilogram = service.create(MeasurementUnitModel.create_kilogram())
    gram = kilogram.base_unit
    replacement = kilogram.clone()
    new_gram = MeasurementUnitModel.create_gram()
    replacement.base_unit = new_gram
    original_file = file_name.read_bytes()

    monkeypatch.setattr(
        "Src.Logics.storage_manager.os.replace",
        Mock(side_effect=OSError("Запись недоступна")),
    )

    # Действия
    with pytest.raises(PersistenceException):
        service.update("measurement_units", kilogram.id, replacement)
    with pytest.raises(NotFoundException):
        manager.get_reference_count(new_gram.id)

    # Проверки
    assert file_name.read_bytes() == original_file
    assert kilogram.base_unit is gram
    assert manager.get_reference_count(gram.id) == 1
    assert manager.get_reference_count(kilogram.id) == 0
    assert len(manager.measurement_units) == 2


def test_storage_persistence__failed_rename__state_order_and_counts_kept(
    persistent_storage, monkeypatch
):
    """Ошибка смены кода сохраняет порядок моделей, общие ссылки и прежние счётчики."""
    # Подготовка
    manager, file_name = persistent_storage
    service = EntityService(manager)
    kilogram = service.create(MeasurementUnitModel.create_kilogram())
    gram = kilogram.base_unit
    service.create(MeasurementUnitModel.create_gram())
    previous_ids = [model.id for model in manager.measurement_units]
    old_id = kilogram.id
    replacement = kilogram.clone()
    replacement.id = "renamed"
    replacement.base_unit = MeasurementUnitModel.create_gram()
    new_gram_id = replacement.base_unit.id
    previous_file = file_name.read_bytes()

    # Действия
    with monkeypatch.context() as patch:
        patch.setattr(
            "Src.Logics.storage_manager.os.replace",
            Mock(side_effect=OSError("Запись недоступна")),
        )
        with pytest.raises(PersistenceException):
            service.update("measurement_units", old_id, replacement)
    with pytest.raises(NotFoundException):
        manager.get_reference_count(new_gram_id)

    # Проверки
    assert file_name.read_bytes() == previous_file
    assert [model.id for model in manager.measurement_units] == previous_ids
    assert manager.get_entity("measurement_units", old_id) is kilogram
    assert manager.find_model("renamed") is None
    assert kilogram.base_unit is gram
    assert manager.get_reference_count(gram.id) == 1
    assert manager.get_reference_count(old_id) == 0


@pytest.mark.parametrize(
    "case",
    ["duplicate_id", "missing_reference", "referenced_delete", "duplicate_delete"],
)
def test_storage_persistence__invalid_incremental_change__file_and_index_kept(
    persistent_storage, case
):
    """Некорректное изменение отклоняется до сохранения файла и индексов."""
    # Подготовка
    manager, file_name = persistent_storage
    kilogram = EntityService(manager).create(MeasurementUnitModel.create_kilogram())
    gram = kilogram.base_unit
    previous_file = file_name.read_bytes()
    added = []
    removed = []
    if case == "duplicate_id":
        added = [gram.clone()]
    elif case == "missing_reference":
        added = [MeasurementUnitModel.create_kilogram()]
    elif case == "duplicate_delete":
        removed = [kilogram, kilogram]
    else:
        removed = [gram]

    # Действия
    with pytest.raises(ConflictException):
        manager.apply_changes(added, removed)

    # Проверки
    assert file_name.read_bytes() == previous_file
    assert len(manager.measurement_units) == 2
    assert manager.get_entity("measurement_units", gram.id) is gram
    assert manager.get_entity("measurement_units", kilogram.id) is kilogram
    assert manager.get_reference_count(gram.id) == 1
    assert manager.get_reference_count(kilogram.id) == 0


@pytest.mark.parametrize("legacy", [False, True])
def test_storage_persistence__organization_restart__settings_use_saved_model(
    tmp_path, legacy
):
    """Настройки получают сохранённую организацию после перезапуска приложения."""
    # Подготовка
    settings = SettingsManager()
    settings.read()
    manager = StorageManager()
    file_name = tmp_path / "storage.json"
    manager.start(settings.settings, str(file_name))
    organization = settings.settings.organization
    extra = organization.clone()
    extra.id = "other-organization"
    extra.name = "Другая организация"
    service = EntityService(manager)
    service.create(extra)
    replacement = organization.clone()
    replacement.name = "Сохранённая"
    service.update("organizations", organization.id, replacement)
    data = json.loads(file_name.read_text(encoding="utf-8"))
    if legacy:
        del data["organization_id"]
    else:
        data["organizations"].reverse()
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    restored = _restart(file_name)
    restored_organization = restored.get_entity("organizations", organization.id)

    # Проверки
    assert restored.settings.organization is restored_organization
    assert restored_organization.name == "Сохранённая"
    assert restored_organization.id == organization.id
    assert restored.get_reference_count(organization.id) == 1


@pytest.mark.parametrize(
    "content",
    [
        "{broken",
        '{"measurement_units": [{"type": "MeasurementUnitModel", '
        '"name": "грамм", "coefficient": 0}]}',
        '{"organizations": [], "organization_id": "missing"}',
    ],
)
def test_storage_persistence__broken_existing_file__startup_rejected(tmp_path, content):
    """Ошибка существующего файла отклоняет запуск и сохраняет исходные данные."""
    # Подготовка
    file_name = tmp_path / "storage.json"
    file_name.write_text(content, encoding="utf-8")
    settings = SettingsModel()
    settings.first_start = True
    manager = StorageManager()

    # Действия
    with pytest.raises(ApplicationException):
        manager.start(settings, str(file_name))

    # Проверки
    assert file_name.read_text(encoding="utf-8") == content
    assert not manager.is_loaded
    assert manager.settings is None
    assert all(manager.get_entities(name) == [] for name in manager.get_entity_types())


def test_storage_persistence__failed_initial_save__startup_can_retry(
    tmp_path, monkeypatch
):
    """Повторный запуск после ошибки первого сохранения создаёт корректное хранилище."""
    # Подготовка
    file_name = tmp_path / "storage.json"
    settings = SettingsModel()
    settings.first_start = True
    manager = StorageManager()

    def fail_replace(source, target) -> None:
        """Имитирует недоступность файла при первом сохранении."""
        raise OSError("Запись недоступна")

    # Действия
    with monkeypatch.context() as patch:
        patch.setattr("Src.Logics.storage_manager.os.replace", fail_replace)
        with pytest.raises(PersistenceException):
            manager.start(settings, str(file_name))
    manager.start(settings, str(file_name))

    # Проверки
    assert manager.is_loaded
    assert manager.measurement_units
    assert file_name.is_file()


def test_storage_persistence__working_directory_change__same_file_updated(
    tmp_path, monkeypatch
):
    """Смена рабочего каталога сохраняет выбранный путь автоматической записи."""
    # Подготовка
    monkeypatch.chdir(tmp_path)
    manager = StorageManager()
    manager.start(SettingsModel(), "data/storage.json")
    other_directory = tmp_path / "other"
    other_directory.mkdir()
    monkeypatch.chdir(other_directory)

    # Действия
    created = EntityService(manager).create(NomenclatureGroupModel.create("Группа"))
    saved = json.loads((tmp_path / "data/storage.json").read_text(encoding="utf-8"))

    # Проверки
    assert saved["nomenclature_groups"][0]["id"] == created.id
    assert not (other_directory / "data").exists()


def test_storage_persistence__renamed_model_reuses_old_id__nested_model_restored(
    persistent_storage,
):
    """Смена кода сохраняет новую вложенную модель со старым кодом после перезапуска."""
    # Подготовка
    manager, file_name = persistent_storage
    service = EntityService(manager)
    gram = service.create(MeasurementUnitModel.create_gram())
    old_id = gram.id
    replacement = MeasurementUnitModel.create_kilogram(gram.clone())
    replacement.id = "kilogram"

    # Действия
    updated = service.update("measurement_units", old_id, replacement)
    nested_before_restart = manager.get_entity("measurement_units", old_id)
    restored = _restart(file_name)
    nested_after_restart = restored.get_entity("measurement_units", old_id)
    restored_kilogram = restored.get_entity("measurement_units", "kilogram")

    # Проверки
    assert updated is gram
    assert updated.base_unit is nested_before_restart
    assert nested_before_restart is not gram
    assert restored_kilogram.base_unit is nested_after_restart
    assert manager.get_reference_count(old_id) == 1
    assert manager.get_reference_count("kilogram") == 0
    assert restored.get_reference_count(old_id) == 1
    assert restored.get_reference_count("kilogram") == 0
    assert len(restored.measurement_units) == len(manager.measurement_units) == 2


def test_storage_persistence__migration_save_failure__startup_can_retry(
    tmp_path, monkeypatch, settings_data
):
    """Ошибка записи после чтения старого файла сохраняет возможность перезапуска."""
    # Подготовка
    file_name = tmp_path / "storage.json"
    legacy = {
        "nomenclature_groups": [
            {"type": "NomenclatureGroupModel", "id": "saved", "name": "Группа"}
        ],
        "organizations": [
            settings_data["organization"]
            | {"id": "saved-organization", "name": "Сохранённая"}
        ],
    }
    file_name.write_text(json.dumps(legacy), encoding="utf-8")
    settings = SettingsManager()
    settings.read()
    original_organization = settings.settings.organization
    manager = StorageManager()

    def fail_replace(source, target) -> None:
        """Имитирует отказ сохранения мигрированного хранилища."""
        raise OSError("Запись недоступна")

    # Действия
    with monkeypatch.context() as patch:
        patch.setattr("Src.Logics.storage_manager.os.replace", fail_replace)
        with pytest.raises(PersistenceException):
            manager.start(settings.settings, str(file_name))
    loaded_after_failure = manager.is_loaded
    file_after_failure = json.loads(file_name.read_text(encoding="utf-8"))
    organization_after_failure = settings.settings.organization
    models_after_failure = manager.get_all_models()
    manager.start(settings.settings, str(file_name))

    # Проверки
    assert not loaded_after_failure
    assert organization_after_failure is original_organization
    assert models_after_failure == []
    assert file_after_failure == legacy
    assert manager.is_loaded
    assert manager.get_entity("nomenclature_groups", "saved").name == "Группа"
    assert manager.settings.organization is manager.get_entities("organizations")[0]
    assert manager.get_reference_count("saved-organization") == 1
