"""Юнит-тесты для Src.Core.common.Common."""

import inspect

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


def test_common__get_constructor_parameters__model__constructor_parameters():
    """Возвращаются параметры конструктора с аннотациями и значениями по умолчанию."""
    # Подготовка
    model_class = MeasurementUnitModel

    # Действия
    parameters = Common.get_constructor_parameters(model_class)

    # Проверки
    assert list(parameters) == ["name", "coefficient", "base_unit"]
    assert parameters["name"].annotation is str
    assert parameters["name"].default is inspect.Parameter.empty
    assert parameters["coefficient"].annotation == int | float
    assert parameters["coefficient"].default is inspect.Parameter.empty
    assert parameters["base_unit"].default is None


def test_common__get_constructor_parameters__inherited_constructor__parameters():
    """Для модели без своего конструктора возвращаются унаследованные параметры."""
    # Подготовка
    model_class = NomenclatureGroupModel

    # Действия
    parameters = Common.get_constructor_parameters(model_class)

    # Проверки
    assert list(parameters) == ["name"]
    assert parameters["name"].annotation is str
    assert parameters["name"].default is inspect.Parameter.empty


@pytest.mark.parametrize("source", [None, 42, "model", str, object])
def test_common__get_constructor_parameters__invalid_source__raises(source):
    """Неверный аргумент вызывает исключение валидации вместо TypeError."""
    # Подготовка
    # Аргумент предоставлен параметризацией.

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Common.get_constructor_parameters(source)

    # Проверки
    assert exc_info.value.field == "source"


def test_common__get_constructor_parameters__model_instance__raises(units):
    """Экземпляр модели вместо класса вызывает исключение валидации."""
    # Подготовка
    source = units["грамм"]

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Common.get_constructor_parameters(source)

    # Проверки
    assert exc_info.value.field == "source"
