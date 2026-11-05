"""Юнит-тесты фабрики десериализации моделей."""

import json

import pytest

from Src.Core.exception import ValidationException
from Src.Logics.deserialize_factory import DeserializeFactory
from Src.Logics.serialize_factory import SerializeFactory
from Src.Models.measurement_unit_model import MeasurementUnitModel


def test_deserialize_factory__saved_units__fields_and_nested_models_restored(units):
    """После чтения JSON восстанавливаются типы, поля и id единиц измерения."""
    # Подготовка
    data = json.loads(json.dumps(SerializeFactory().convert(units)))

    # Действия
    restored = DeserializeFactory().convert(data)

    # Проверки
    assert list(restored) == list(units)
    for name, original in units.items():
        loaded = restored[name]
        assert type(loaded) is MeasurementUnitModel
        assert loaded is not original
        assert loaded.id == original.id
        assert loaded.name == original.name
        assert loaded.coefficient == original.coefficient
        assert loaded.base_coefficient == original.base_coefficient
        if original.base_unit is None:
            assert loaded.base_unit is None
        else:
            assert type(loaded.base_unit) is MeasurementUnitModel
            assert loaded.base_unit.id == original.base_unit.id
            assert loaded.base_unit.name == original.base_unit.name
            assert loaded.base_unit.coefficient == original.base_unit.coefficient
            assert loaded.base_unit.base_unit is None


def test_deserialize_factory__optional_argument_absent__constructor_default_used():
    """Отсутствующий base_unit получает значение по умолчанию из конструктора."""
    # Подготовка
    data = {"type": "MeasurementUnitModel", "name": "грамм", "coefficient": 1}

    # Действия
    model = DeserializeFactory().convert(data)

    # Проверки
    assert model.name == "грамм"
    assert model.coefficient == 1
    assert model.base_unit is None
    assert model.id


@pytest.mark.parametrize("field", ["name", "coefficient"])
def test_deserialize_factory__required_argument_absent__raises(field):
    """Отсутствующий обязательный аргумент вызывает ошибку с именем поля."""
    # Подготовка
    data = {"type": "MeasurementUnitModel", "name": "грамм", "coefficient": 1}
    del data[field]

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        DeserializeFactory().convert(data)

    # Проверки
    assert exc_info.value.field == field


@pytest.mark.parametrize("type_name", ["UnknownModel", None, [], {}])
def test_deserialize_factory__invalid_model_type__raises(type_name):
    """Неизвестный или некорректный тип модели вызывает ошибку валидации."""
    # Подготовка
    data = {"type": type_name}

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        DeserializeFactory().convert(data)

    # Проверки
    assert exc_info.value.field == "type"


def test_deserialize_factory__nested_collections__structure_and_values_kept():
    """Обычные словари, списки и простые значения JSON сохраняют структуру."""
    # Подготовка
    data = {"values": [None, True, False, 1, 1.5, "текст", [], {}]}

    # Действия
    restored = DeserializeFactory().convert(data)

    # Проверки
    assert restored == data


@pytest.mark.parametrize(
    ("field", "value"), [("coefficient", 0), ("id", ""), ("base_unit", "грамм")]
)
def test_deserialize_factory__invalid_model_field__validation_preserved(field, value):
    """Конструктор и сеттер id продолжают проверять загруженные значения."""
    # Подготовка
    data = {"type": "MeasurementUnitModel", "name": "грамм", "coefficient": 1}
    data[field] = value

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        DeserializeFactory().convert(data)

    # Проверки
    assert exc_info.value.field == field


def test_deserialize_factory__non_json_object__raises():
    """Объект вне формата JSON вызывает ошибку валидации источника."""
    # Подготовка
    source = object()

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        DeserializeFactory().convert(source)

    # Проверки
    assert exc_info.value.field == "source"
