"""Юнит-тесты для Src.Core.named_entity.named_entity."""
import pytest

from Src.Core.named_entity import named_entity
from Src.Core.exception import validation_exception


class _named_entity(named_entity):
  """Заглушка-наследник для тестирования named_entity."""
  pass


def test_NameIsSet_Constructor_ValidNameAccepted():
  """При создании с валидным именем оно сохраняется без ошибок."""
  entity = _named_entity("Ромашка")
  assert entity.name == "Ромашка"


def test_ValidationException_Constructor_EmptyStringRaises():
  """Пустая строка в качестве имени вызывает исключение валидации."""
  with pytest.raises(validation_exception):
    _named_entity("")


def test_ValidationException_Constructor_NoneRaises():
  """None в качестве имени вызывает исключение валидации."""
  with pytest.raises(validation_exception):
    _named_entity(None)


def test_ValidationException_Constructor_NonStringRaises():
  """Не строковое значение имени вызывает исключение валидации."""
  with pytest.raises(validation_exception):
    _named_entity(123)


def test_NameIsUpdated_NameSetter_ValidNameAccepted():
  """Сеттер имени принимает валидное значение и обновляет свойство."""
  entity = _named_entity("Ромашка")
  entity.name = "Одуванчик"
  assert entity.name == "Одуванчик"


def test_ValidationException_NameSetter_InvalidNameRaises():
  """Сеттер имени вызывает исключение валидации на невалидном значении."""
  entity = _named_entity("Ромашка")
  with pytest.raises(validation_exception):
    entity.name = ""
