"""Проверки операций сервиса над доменными моделями без обработки JSON."""

from copy import copy

import pytest

from Src.Core.exception import ConflictException, ValidationException
from Src.Logics.entity_service import EntityService
from Src.Logics.model_registry import ENTITY_TYPES
from Src.Logics.storage_manager import StorageManager
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.settings_model import SettingsModel


def test_entity_service__model_crud__changes_applied():
    """Сервис создаёт, изменяет и удаляет модели без словарей запросов."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    model = NomenclatureGroupModel("Группа")
    replacement = NomenclatureGroupModel("Новое имя")
    replacement.id = model.id

    # Действия
    created = service.create(model)
    updated = service.update("nomenclature_groups", created.id, replacement)
    updated_name = created.name
    service.delete("nomenclature_groups", created.id)

    # Проверки
    assert updated is created
    assert updated_name == "Новое имя"
    assert model.name == "Группа"
    assert storage.nomenclature_groups == []


def test_entity_service__matching_nested_model__stored_instance_reused():
    """Совпадающая вложенная модель связывается с существующим экземпляром."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    gram = service.create(MeasurementUnitModel.create_gram())
    detached = copy(gram)
    candidate = MeasurementUnitModel.create_kilogram(detached)

    # Действия
    kilogram = service.create(candidate)
    replacement = copy(gram)
    replacement.name = "Общая единица"
    updated = service.update("measurement_units", gram.id, replacement)

    # Проверки
    assert kilogram.base_unit is gram
    assert updated is gram
    assert kilogram.base_unit.name == "Общая единица"
    assert candidate.base_unit is detached
    assert detached.name == "грамм"
    assert len(storage.measurement_units) == 2


def test_entity_service__conflicting_nested_model__graph_kept():
    """Противоречивое вложенное описание отклоняется без изменения ссылок."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    kilogram = service.create(MeasurementUnitModel.create_kilogram())
    conflicting = MeasurementUnitModel("килограмм", 1)
    conflicting.id = kilogram.id
    candidate = MeasurementUnitModel("тонна", 1000, conflicting)

    # Действия
    with pytest.raises(ConflictException):
        service.create(candidate)

    # Проверки
    assert len(storage.measurement_units) == 2
    assert kilogram.coefficient == 1000
    assert kilogram.base_unit is not None
    assert candidate.base_unit is conflicting


@pytest.mark.parametrize("model", [None, {"name": "Группа"}, SettingsModel()])
def test_entity_service__unsupported_model__validation_error(model):
    """Сервис отклоняет JSON и модели, не зарегистрированные как доменные."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)

    # Действия
    with pytest.raises(ValidationException):
        service.create(model)

    # Проверки
    assert storage.get_all_models() == []


def test_entity_service__duplicate_id__original_model_kept():
    """Создание модели с занятым кодом отклоняется независимо от её класса."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    original = service.create(NomenclatureGroupModel("Группа"))
    candidate = MeasurementUnitModel.create_gram()
    candidate.id = original.id

    # Действия
    with pytest.raises(ConflictException):
        service.create(candidate)

    # Проверки
    assert storage.get_all_models() == [original]
    assert storage.get_entity("nomenclature_groups", original.id) is original


def test_entity_service__wrong_replacement_type__original_model_kept():
    """Изменение не позволяет заменить модель объектом другого класса."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    original = service.create(NomenclatureGroupModel("Группа"))

    # Действия
    with pytest.raises(ValidationException):
        service.update(
            "nomenclature_groups", original.id, MeasurementUnitModel.create_gram()
        )

    # Проверки
    assert storage.get_entity("nomenclature_groups", original.id) is original
    assert original.name == "Группа"
    assert storage.measurement_units == []


@pytest.mark.parametrize("operation", ["delete", "rename"])
def test_entity_service__incoming_reference__operation_rejected(operation):
    """Входящая ссылка запрещает удаление модели и изменение её кода."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    gram = service.create(MeasurementUnitModel.create_gram())
    kilogram = service.create(MeasurementUnitModel.create_kilogram(gram))
    replacement = copy(gram)
    replacement.id = "new-code"

    # Действия
    with pytest.raises(ConflictException):
        if operation == "delete":
            service.delete("measurement_units", gram.id)
        else:
            service.update("measurement_units", gram.id, replacement)

    # Проверки
    assert storage.get_entity("measurement_units", gram.id) is gram
    assert kilogram.base_unit is gram


def test_entity_service__cyclic_model__graph_not_saved():
    """Циклическая модель отклоняется до сохранения и не меняет хранилище."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    gram = MeasurementUnitModel.create_gram()
    gram.base_unit = gram

    # Действия
    with pytest.raises(ConflictException):
        service.create(gram)

    # Проверки
    assert storage.measurement_units == []
    assert gram.base_unit is gram


def test_entity_service__readonly_nested_model__stored_instance_reused(monkeypatch):
    """Вложенная модель без сеттера также связывается с общим экземпляром."""

    # Подготовка
    class ExtraGroupModel(NomenclatureGroupModel):
        """Дополнительная модель с неизменяемой ссылкой на единицу измерения."""

        def __init__(self, name: str, unit: MeasurementUnitModel) -> None:
            """Создаёт группу со вложенной единицей измерения."""
            super().__init__(name)
            self.__unit = unit

        @property
        def unit(self) -> MeasurementUnitModel:
            """Возвращает единицу измерения группы."""
            return self.__unit

    monkeypatch.setitem(ENTITY_TYPES, "extra_groups", ExtraGroupModel)
    storage = StorageManager()
    service = EntityService(storage)
    gram = service.create(MeasurementUnitModel.create_gram())
    candidate = ExtraGroupModel("Группа", copy(gram))

    # Действия
    created = service.create(candidate)

    # Проверки
    assert created.unit is gram
    assert candidate.unit is not gram
    assert len(storage.measurement_units) == 1
    assert storage.get_entity("extra_groups", created.id) is created
