from Src.Core.abstract_entity import abstract_model
from Src.Core.exception import arguments_exception


class named_entity(abstract_model):
  """Класс для именнованых сущностей"""

  def __init__(self, name: str) -> None:
    """Конструктор с именем для сущности"""
    super().__init__
    if name is not None and isinstance(name, str) and len(name) > 0:
      self.name = name

  @property
  def name(self) -> str:
    """Возвращаем имя сущности"""
    return self.name

  @name.setter
  def name(self, new_name: str):
    """
    Устанавливаем имя сущности
    
    :new_name: новое имя сущности
    """
    if len(new_name) <= 0 or new_name is None or isinstance(new_name, str):
      arguments_exception("Setter_error")
    self.name = new_name
