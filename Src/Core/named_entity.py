from Src.Core.abstract_entity import abstract_model
from Src.Core.exception import arguments_exception


class named_entity(abstract_model):
  """Класс для именнованых сущностей"""

  def __init__(self, name: str) -> None:
    """Конструктор с именем для сущности"""
    super().__init__()
    self._validate_name(name)
    self.__name = name

  @property
  def name(self) -> str:
    """Возвращаем имя сущности"""
    return self.__name

  @name.setter
  def name(self, new_name: str):
    """
    Устанавливаем имя сущности
    
    :new_name: новое имя сущности
    """
    self._validate_name(new_name)
    self.name = new_name


  def _validate_name(self, value: str) -> None:
      """Базовая проверка имени. Подклассы могут расширять через super()."""
      if value is None or not isinstance(value, str) or len(value) == 0:
          raise arguments_exception("name", "Имя не должно быть пустым")
