"""Юнит-тесты для Src.Core.abstract_model.AbstractModel."""

import pytest

from Src.Core.abstract_model import AbstractModel
from Src.Core.exception import ValidationException


class _AbstractModelStub(AbstractModel):
    """Заглушка-наследник для тестирования AbstractModel."""


def test_abstract_model__constructor__id_is_not_empty():
    """При создании сущности id сразу не пустой."""
    # Подготовка
    # Дополнительная подготовка не требуется.

    # Действия
    entity = _AbstractModelStub()

    # Проверки
    assert entity.id is not None
    assert entity.id != ""


def test_abstract_model__constructor__ids_are_different_across_instances():
    """Два новых экземпляра получают разные id."""
    # Подготовка
    entity1 = _AbstractModelStub()

    # Действия
    entity2 = _AbstractModelStub()

    # Проверки
    assert entity1.id != entity2.id


def test_abstract_model__eq__different_id_instances_are_not_equal():
    """Сущности с разным id не считаются равными."""
    # Подготовка
    entity1 = _AbstractModelStub()
    entity2 = _AbstractModelStub()

    # Действия
    result = entity1 == entity2

    # Проверки
    assert not result


def test_abstract_model__set_id__id_replaced():
    """Установленный id заменяет сгенерированный, пробелы по краям обрезаются."""
    # Подготовка
    entity = _AbstractModelStub()

    # Действия
    entity.id = "  257a7811-be66-4b35-8e81-a04226fecc2d "

    # Проверки
    assert entity.id == "257a7811-be66-4b35-8e81-a04226fecc2d"


@pytest.mark.parametrize("new_id", [None, "", "   ", 42])
def test_abstract_model__set_invalid_id__raises(new_id):
    """Пустой id или id не строкой вызывает исключение валидации."""
    # Подготовка
    entity = _AbstractModelStub()

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        entity.id = new_id

    # Проверки
    assert isinstance(exc_info.value, ValidationException)
