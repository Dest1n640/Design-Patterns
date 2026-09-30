from abc import ABC


class AbstractManager(ABC):
  """Абстрактный класс настроек"""
  _file_name: str = ""
  _is_loaded: bool = False
  _data: list = []

  def load(self, file_name: str = "") -> None:
    """Метод загрузки данных"""
    pass

  def convert(self) -> bool:
    """Обработка загруженных данных"""
    return False

  def is_loaded(self) -> bool:
    """Проверка на загрузку данных"""
    return self._is_loaded
