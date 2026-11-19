"""Юнит-тесты для Src.Core.common.Common."""

from typing import Self

import pytest

from Src.Core.common import Common
from Src.Core.exception import ValidationException
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.technological_map_model import TechnologicalMapModel


def test_common__get_fields__public_properties_only(units):
    """Возвращаются только публичные свойства, без методов и закрытых полей."""
    # Подготовка
    kilogram = units["килограмм"]

    # Действия
    fields = Common.get_fields(kilogram)

    # Проверки
    assert fields == [
        "base_coefficient",
        "base_unit",
        "coefficient",
        "id",
        "name",
    ]


def test_common__get_fields_is_common__lists_excluded(groups, units):
    """С is_common=True свойства-списки исключаются."""
    # Подготовка
    recipe = TechnologicalMapModel.create_technological_map(groups, units)

    # Действия
    all_fields = Common.get_fields(recipe)
    common_fields = Common.get_fields(recipe, is_common=True)

    # Проверки
    assert all_fields == ["dishes", "id", "name"]
    assert common_fields == ["id", "name"]


def test_common__get_fields_none__raises():
    """None вместо модели вызывает исключение валидации."""
    # Подготовка
    model = None

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Common.get_fields(model)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_common_get_field_types__model__setter_annotations_returned():
    """Типы полей определяются сеттерами без анализа конструктора."""
    # Подготовка
    model_class = MeasurementUnitModel

    # Действия
    fields = Common.get_field_types(model_class)

    # Проверки
    assert fields == {
        "base_unit": Self | None,
        "coefficient": int | float,
        "id": str,
        "name": str,
    }


def test_common_get_field_types__inherited_properties__annotations_returned():
    """Для модели без собственных свойств возвращаются унаследованные сеттеры."""
    # Подготовка
    model_class = NomenclatureGroupModel

    # Действия
    fields = Common.get_field_types(model_class)

    # Проверки
    assert fields == {"id": str, "name": str}


@pytest.mark.parametrize("source", [None, 42, "model"])
def test_common_get_field_types__invalid_source__raises(source):
    """Неверный аргумент вызывает исключение валидации вместо TypeError."""
    # Подготовка
    # Аргумент предоставлен параметризацией.

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Common.get_field_types(source)

    # Проверки
    assert exc_info.value.field == "source"


def test_common_get_field_types__model_instance__raises(units):
    """Экземпляр модели вместо класса вызывает исключение валидации."""
    # Подготовка
    source = units["грамм"]

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Common.get_field_types(source)

    # Проверки
    assert exc_info.value.field == "source"
