"""Юнит-тесты для Src.Core.named_entity.named_entity."""
import pytest

from Src.Core.named_entity import named_entity
from Src.Core.exception import validation_exception


class _named_entity(named_entity):
  """Заглушка-наследник для тестирования named_entity."""
  pass


def test_name_is_set_constructor_valid_name_accepted():
  """При создании с валидным именем оно сохраняется без ошибок."""
  entity = _named_entity("Ромашка")
  assert entity.name == "Ромашка"


def test_validation_exception_constructor_empty_string_raises():
  """Пустая строка в качестве имени вызывает исключение валидации."""
  with pytest.raises(validation_exception):
    _named_entity("")


def test_validation_exception_constructor_none_raises():
  """None в качестве имени вызывает исключение валидации."""
  with pytest.raises(validation_exception):
    _named_entity(None)


def test_validation_exception_constructor_non_string_raises():
  """Не строковое значение имени вызывает исключение валидации."""
  with pytest.raises(validation_exception):
    _named_entity(123)


def test_name_is_updated_name_setter_valid_name_accepted():
  """Сеттер имени принимает валидное значение и обновляет свойство."""
  entity = _named_entity("Ромашка")
  entity.name = "Одуванчик"
  assert entity.name == "Одуванчик"


def test_validation_exception_name_setter_invalid_name_raises():
  """Сеттер имени вызывает исключение валидации на невалидном значении."""
  entity = _named_entity("Ромашка")
  with pytest.raises(validation_exception):
    entity.name = ""
