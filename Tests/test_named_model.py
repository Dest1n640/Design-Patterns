"""Юнит-тесты для Src.Core.named_model.NamedModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel


class _NamedModelStub(NamedModel):
    """Заглушка-наследник для тестирования NamedModel."""


def test_named_model__constructor__valid_name_is_set():
    """При создании с валидным именем оно сохраняется без ошибок."""
    entity = _NamedModelStub("Ромашка")
    assert entity.name == "Ромашка"


def test_named_model__constructor__empty_string_raises_validation_exception():
    """Пустая строка в качестве имени вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _NamedModelStub("")


def test_named_model__constructor__none_raises_validation_exception():
    """None в качестве имени вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _NamedModelStub(None)


def test_named_model__constructor__non_string_raises_validation_exception():
    """Не строковое значение имени вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _NamedModelStub(123)


def test_named_model__name_setter__valid_name_is_updated():
    """Сеттер имени принимает валидное значение и обновляет свойство."""
    entity = _NamedModelStub("Ромашка")
    entity.name = "Одуванчик"
    assert entity.name == "Одуванчик"


def test_named_model__name_setter__invalid_name_raises_validation_exception():
    """Сеттер имени вызывает исключение валидации на невалидном значении."""
    entity = _NamedModelStub("Ромашка")
    with pytest.raises(ValidationException):
        entity.name = ""
