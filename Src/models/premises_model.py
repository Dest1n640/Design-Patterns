from Src.Core.named_entity import named_entity
from Src.Core.exception import validation_exception

class premises_model(named_entity):
  """Класс помещения, в котором расположен склад"""

  def __init__(self, name: str, address: str, square: int | float):
    """
    Конструктор помещения

    :address: адрес помещения
    :square: площадь помещения
    """
    super().__init__(name)
    self.address = address
    self.square = square

  @property
  def address(self):
    """Возвращает адрес помещения"""
    return self.__address

  @property
  def square(self):
    """Возвращает площадь помещения"""
    return self.__square

  @address.setter
  def address(self, new_address: str):
    """
    Устанавливает адрес помещения

    :new_address: новый адрес помещения
    """
    self._validate_address(new_address)
    self.__address = new_address

  @square.setter
  def square(self, new_square: int | float):
    """
    Устанавливает площадь помещения

    :new_square: новая площадь помещения
    """
    self._validate_square(new_square)
    self.__square = new_square

  def _validate_address(self, value: str) -> None:
    """
    Проверка адреса помещения: непустая строка

    :value: проверяемый адрес
    """
    if value is None or not isinstance(value, str) or len(value) == 0:
      raise validation_exception("address", "Адрес не должен быть пустым")

  def _validate_square(self, value: int | float) -> None:
    """
    Проверка площади помещения: положительное число

    :value: проверяемая площадь
    """
    if not isinstance(value, int | float) or value <= 0:
      raise validation_exception("square", "Площадь должна быть положительным числом")

