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


@pytest.mark.parametrize("order", [("грамм", "килограмм"), ("килограмм", "грамм")])
def test_deserialize_factory__repeated_id__shared_instance_restored(units, order):
    """Вложенная и самостоятельная модели с одним id становятся одним объектом."""
    # Подготовка
    source = SerializeFactory().convert([units[name] for name in order])

    # Действия
    restored = DeserializeFactory().convert(source)
    by_name = {model.name: model for model in restored}

    # Проверки
    assert by_name["килограмм"].base_unit is by_name["грамм"]


def test_deserialize_factory__equivalent_fields__shared_instance_restored():
    """Очистка строк и значения по умолчанию учитываются при сравнении моделей."""
    # Подготовка
    source = [
        {
            "type": "MeasurementUnitModel",
            "id": " unit ",
            "name": " грамм ",
            "coefficient": 1,
        },
        {
            "type": "MeasurementUnitModel",
            "id": "unit",
            "name": "грамм",
            "coefficient": 1.0,
            "base_unit": None,
        },
    ]

    # Действия
    restored = DeserializeFactory().convert(source)

    # Проверки
    assert restored[0] is restored[1]


@pytest.mark.parametrize(
    "changes", [{"name": "Другое название"}, {"type": "NomenclatureGroupModel"}]
)
def test_deserialize_factory__conflicting_id__raises(changes):
    """Различия данных или типов при одинаковом id вызывают ошибку валидации."""
    # Подготовка
    source = {
        "type": "MeasurementUnitModel",
        "id": "unit",
        "name": "грамм",
        "coefficient": 1,
    }

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        DeserializeFactory().convert([source, source | changes])

    # Проверки
    assert exc_info.value.field == "id"


def test_deserialize_factory__nested_ancestor_id__raises():
    """Повтор кода предка во вложенной модели отклоняется как противоречие."""
    # Подготовка
    unit = {
        "type": "MeasurementUnitModel",
        "id": "unit",
        "name": "грамм",
        "coefficient": 1,
    }
    source = unit | {"base_unit": unit}

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        DeserializeFactory().convert(source)

    # Проверки
    assert exc_info.value.field == "id"


def test_deserialize_factory__separate_calls__independent_graphs_restored():
    """Повторное использование фабрики создаёт независимый граф моделей."""
    # Подготовка
    factory = DeserializeFactory()
    source = {"type": "NomenclatureGroupModel", "id": "group", "name": "Группа"}
    first = factory.convert(source)

    # Действия
    second = factory.convert(source | {"name": "Новое название"})

    # Проверки
    assert first is not second
    assert first.name == "Группа"
    assert second.name == "Новое название"
    assert factory.models[0] is second


def test_deserialize_factory__failed_conversion__previous_models_kept():
    """Ошибка десериализации сохраняет результат предыдущего успешного вызова."""
    # Подготовка
    factory = DeserializeFactory()
    source = {"type": "NomenclatureGroupModel", "id": "group", "name": "Группа"}
    original = factory.convert(source)

    # Действия
    with pytest.raises(ValidationException):
        factory.convert([source, source | {"name": "Конфликт"}])

    # Проверки
    assert len(factory.models) == 1
    assert factory.models[0] is original


def test_deserialize_factory__unused_nested_field__extra_model_ignored():
    """Неиспользуемое поле входных данных не добавляет сущность в граф модели."""
    # Подготовка
    factory = DeserializeFactory()
    source = {
        "type": "NomenclatureGroupModel",
        "name": "Группа",
        "extra": {"type": "RestaurantModel", "name": "Ресторан"},
    }

    # Действия
    model = factory.convert(source)

    # Проверки
    assert len(factory.models) == 1
    assert factory.models[0] is model
