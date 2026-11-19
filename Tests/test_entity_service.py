"""Проверки операций сервиса над доменными моделями без обработки JSON."""

import pytest

from Src.Core.exception import ConflictException, ValidationException
from Src.Core.validation import Validation
from Src.Logics.entity_service import EntityService
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.settings_model import SettingsModel


def _change_unit(
    service: EntityService,
    model: MeasurementUnitModel,
    replacement: MeasurementUnitModel,
    operation: str,
) -> None:
    """Выполняет проверяемое удаление единицы измерения или смену её кода."""
    if operation == "delete":
        service.delete("measurement_units", model.id)
    else:
        service.update("measurement_units", model.id, replacement)


def test_entity_service__model_crud__changes_applied():
    """Сервис создаёт, изменяет и удаляет модели без словарей запросов."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    model = NomenclatureGroupModel.create("Группа")
    replacement = NomenclatureGroupModel.create("Новое имя")
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
    detached = gram.clone()
    candidate = MeasurementUnitModel.create_kilogram(detached)

    # Действия
    kilogram = service.create(candidate)
    replacement = gram.clone()
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
    conflicting = MeasurementUnitModel.create("килограмм", 1)
    conflicting.id = kilogram.id
    candidate = MeasurementUnitModel.create("тонна", 1000, conflicting)

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
    original = service.create(NomenclatureGroupModel.create("Группа"))
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
    original = service.create(NomenclatureGroupModel.create("Группа"))

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
    replacement = gram.clone()
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


def test_entity_service__new_nested_model__stored_instance_reused(
    register_entity_type,
):
    """Новая модель со вложенным объектом связывается с общим экземпляром."""

    # Подготовка
    class ExtraGroupModel(NomenclatureGroupModel):
        """Дополнительная модель со ссылкой на единицу измерения."""

        def __init__(self) -> None:
            """Создаёт группу без заполненных свойств."""
            super().__init__()
            self.__unit = None

        @property
        def unit(self) -> MeasurementUnitModel:
            """Возвращает единицу измерения группы."""
            return self.__unit

        @unit.setter
        def unit(self, value: MeasurementUnitModel) -> None:
            """Устанавливает единицу измерения группы."""
            self.__unit = Validation.validate_instance(
                value, MeasurementUnitModel, "unit", "Ожидается единица измерения"
            )

    register_entity_type("extra_groups", ExtraGroupModel)
    storage = StorageManager()
    service = EntityService(storage)
    gram = service.create(MeasurementUnitModel.create_gram())
    candidate = ExtraGroupModel()
    candidate.name = "Группа"
    candidate.unit = gram.clone()

    # Действия
    created = service.create(candidate)

    # Проверки
    assert created.unit is gram
    assert candidate.unit is not gram
    assert len(storage.measurement_units) == 1
    assert storage.get_entity("extra_groups", created.id) is created


def test_entity_service__unfilled_model__storage_kept():
    """Сервис отклоняет незаполненную модель до изменения хранилища."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    model = NomenclatureGroupModel()

    # Действия
    with pytest.raises(ValidationException):
        service.create(model)

    # Проверки
    assert storage.get_all_models() == []
    assert model.name == ""


@pytest.mark.parametrize("operation", ["delete", "rename"])
def test_entity_service__multiple_owners__blocked_until_last_reference_removed(
    operation,
):
    """Каждый владелец удерживает общую модель до удаления последней ссылки."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    gram = service.create(MeasurementUnitModel.create_gram())
    kilogram = service.create(MeasurementUnitModel.create_kilogram(gram.clone()))
    tonne = service.create(MeasurementUnitModel.create("тонна", 1000000, gram.clone()))
    replacement = gram.clone()
    replacement.id = "new-gram"

    # Действия
    with pytest.raises(ConflictException):
        _change_unit(service, gram, replacement, operation)
    service.delete("measurement_units", kilogram.id)
    with pytest.raises(ConflictException):
        _change_unit(service, gram, replacement, operation)
    service.delete("measurement_units", tonne.id)
    _change_unit(service, gram, replacement, operation)
    remaining = storage.measurement_units

    # Проверки
    assert kilogram.base_unit is gram
    assert tonne.base_unit is gram
    if operation == "delete":
        assert remaining == []
    else:
        assert len(remaining) == 1
        assert storage.get_entity("measurement_units", replacement.id) is gram


@pytest.mark.parametrize("container_type", [list, dict])
def test_entity_service__repeated_nested_reference__replacement_releases_links(
    link_model_type, container_type
):
    """Повторы модели сохраняют один экземпляр и освобождаются заменой коллекции."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    gram = service.create(MeasurementUnitModel.create_gram())
    owner = link_model_type.create("Владелец")
    owner.links = (
        [gram, gram.clone()]
        if container_type is list
        else {"first": [gram], "second": {"unit": gram.clone()}}
    )

    # Действия
    created = service.create(owner)
    registered_units = storage.measurement_units
    original_links = created.links
    initial_count = storage.get_reference_count(gram.id)
    replacement = created.clone()
    replacement.links = (
        [gram] if container_type is list else {"remaining": {"unit": gram}}
    )
    service.update("links", created.id, replacement)
    remaining_count = storage.get_reference_count(gram.id)
    with pytest.raises(ConflictException):
        service.delete("measurement_units", gram.id)
    replacement = created.clone()
    replacement.links = container_type()
    service.update("links", created.id, replacement)
    released_count = storage.get_reference_count(gram.id)
    service.delete("measurement_units", gram.id)

    # Проверки
    assert len(registered_units) == 1
    assert registered_units[0] is gram
    assert (initial_count, remaining_count, released_count) == (2, 1, 0)
    if container_type is list:
        assert all(link is gram for link in original_links)
    else:
        assert original_links["first"][0] is gram
        assert original_links["second"]["unit"] is gram
    assert storage.measurement_units == []
    assert storage.get_entity("links", created.id) is created
    assert created.links == container_type()


def test_entity_service__source_collections_changed__stored_graph_kept(link_model_type):
    """Изменение исходных вложенных коллекций сохраняет зарегистрированный граф."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    gram = MeasurementUnitModel.create_gram()
    source = link_model_type.create("Владелец")
    source.links = {"units": [gram], "names": ["Исходное"]}

    # Действия
    created = service.create(source)
    source.links["units"].clear()
    source.links["names"].append("Новое")

    # Проверки
    stored_gram = storage.get_entity("measurement_units", gram.id)
    assert stored_gram is not gram
    assert created.links["units"][0] is stored_gram
    assert created.links["names"] == ["Исходное"]
    assert storage.get_reference_count(gram.id) == 1


def test_entity_service__nested_chain__each_owner_keeps_its_direct_reference():
    """Удаление вершины цепочки сохраняет вложенные модели и связи между ними."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    tonne = service.create(
        MeasurementUnitModel.create(
            "тонна", 1000, MeasurementUnitModel.create_kilogram()
        )
    )
    kilogram = tonne.base_unit
    gram = kilogram.base_unit

    # Действия
    registered_units = storage.measurement_units
    service.delete("measurement_units", tonne.id)
    retained_kilogram = storage.get_entity("measurement_units", kilogram.id)
    with pytest.raises(ConflictException):
        service.delete("measurement_units", gram.id)
    service.delete("measurement_units", kilogram.id)
    service.delete("measurement_units", gram.id)

    # Проверки
    assert len(registered_units) == 3
    assert retained_kilogram is kilogram
    assert retained_kilogram.base_unit is gram
    assert storage.measurement_units == []


def test_entity_service__shared_nested_owner__only_direct_counts_changed():
    """Новые владельцы общей модели изменяют только счётчик непосредственной ссылки."""
    # Подготовка
    storage = StorageManager()
    service = EntityService(storage)
    kilogram = service.create(MeasurementUnitModel.create_kilogram())
    gram = kilogram.base_unit

    # Действия
    first = service.create(MeasurementUnitModel.create("Первая", 2, kilogram.clone()))
    second = service.create(MeasurementUnitModel.create("Вторая", 3, kilogram.clone()))
    created_counts = (
        storage.get_reference_count(gram.id),
        storage.get_reference_count(kilogram.id),
    )
    service.delete("measurement_units", first.id)
    first_deleted_counts = (
        storage.get_reference_count(gram.id),
        storage.get_reference_count(kilogram.id),
    )
    service.delete("measurement_units", second.id)
    owners_deleted_counts = (
        storage.get_reference_count(gram.id),
        storage.get_reference_count(kilogram.id),
    )
    service.delete("measurement_units", kilogram.id)

    # Проверки
    assert created_counts == (1, 2)
    assert first_deleted_counts == (1, 1)
    assert owners_deleted_counts == (1, 0)
    assert storage.get_reference_count(gram.id) == 0
    assert storage.measurement_units == [gram]


@pytest.mark.parametrize("operation", ["delete", "rename"])
def test_entity_service__settings_reference__organization_code_protected(operation):
    """Ссылка из настроек запрещает удаление организации и смену её кода."""
    # Подготовка
    settings_manager = SettingsManager()
    settings_manager.read()
    settings = settings_manager.settings
    settings.first_start = False
    storage = StorageManager()
    storage.start(settings)
    service = EntityService(storage)
    organization = settings.organization
    replacement = organization.clone()
    replacement.id = "new-organization"

    # Действия
    with pytest.raises(ConflictException):
        if operation == "delete":
            service.delete("organizations", organization.id)
        else:
            service.update("organizations", organization.id, replacement)

    # Проверки
    assert settings.organization is organization
    assert storage.get_entity("organizations", organization.id) is organization
    assert storage.get_all_models() == [organization]
