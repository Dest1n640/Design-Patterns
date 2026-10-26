"""Юнит-тесты для Src.Core.abstract_model.AbstractModel."""

import pytest

from Src.Core.abstract_model import AbstractModel
from Src.Core.exception import ValidationException


class _AbstractModelStub(AbstractModel):
    """Заглушка-наследник для тестирования AbstractModel."""


def test_abstract_model__constructor__id_is_not_empty():
    """При создании сущности id сразу не пустой."""
    entity = _AbstractModelStub()
    assert entity.id is not None
    assert entity.id != ""


def test_abstract_model__constructor__ids_are_different_across_instances():
    """Два новых экземпляра получают разные id."""
    entity1 = _AbstractModelStub()
    entity2 = _AbstractModelStub()
    assert entity1.id != entity2.id


def test_abstract_model__eq__different_id_instances_are_not_equal():
    """Сущности с разным id не считаются равными."""
    entity1 = _AbstractModelStub()
    entity2 = _AbstractModelStub()
    assert entity1 != entity2


def test_abstract_model__set_id__id_replaced():
    """Установленный id заменяет сгенерированный, пробелы по краям обрезаются."""
    entity = _AbstractModelStub()

    entity.id = "  257a7811-be66-4b35-8e81-a04226fecc2d "

    assert entity.id == "257a7811-be66-4b35-8e81-a04226fecc2d"


@pytest.mark.parametrize("new_id", [None, "", "   ", 42])
def test_abstract_model__set_invalid_id__raises(new_id):
    """Пустой id или id не строкой вызывает исключение валидации."""
    entity = _AbstractModelStub()

    with pytest.raises(ValidationException):
        entity.id = new_id
