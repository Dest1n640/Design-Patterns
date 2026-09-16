from abc import ABC, abstractmethod
from uuid import UUID, uuid4


class identify(ABC):
    """Абстрактный базовый класс для идентифицируемых сущностей."""

    def __init__(self) -> None:
        """Инициализирует базовый экземпляр сущности."""
        self.__name = ""
        self.__id = uuid4()
    
    @property
    def id(self) -> UUID:
        """Возвращает уникальный идентификатор сущности."""
        return self.__id

    @property
    def name(self) -> str:
        """Возвращает наименование сущности."""
        return self.__name

    @name.setter
    def name(self, new_name: str) -> None:
        """
        Устанавливает наименование сущности.

        :param value: Новое наименование сущности.
        """
        if new_name is not None and len(new_name) > 0 and isinstance(new_name, str):
          self.__name = new_name
