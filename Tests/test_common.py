"""Юнит-тесты для Src.Core.common.Common."""

import pytest

from Src.Core.common import Common
from Src.Core.exception import ValidationException
from Src.Models.technological_map_model import TechnologicalMapModel


def test_common__get_fields__public_properties_only(units):
    """Возвращаются только публичные свойства, без методов и закрытых полей."""
    assert Common.get_fields(units["килограмм"]) == [
        "base_coefficient",
        "base_unit",
        "coefficient",
        "id",
        "name",
    ]


def test_common__get_fields_is_common__lists_excluded(groups, units):
    """С is_common=True свойства-списки исключаются."""
    recipe = TechnologicalMapModel.create_technological_map(groups, units)

    assert Common.get_fields(recipe) == ["dishes", "id", "name"]
    assert Common.get_fields(recipe, is_common=True) == ["id", "name"]


def test_common__get_fields_none__raises():
    """None вместо модели вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        Common.get_fields(None)
