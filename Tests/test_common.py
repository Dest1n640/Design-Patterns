"""Юнит-тесты для Src.Core.common.Common."""

import pytest

from Src.Core.common import Common
from Src.Core.exception import ValidationException
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
