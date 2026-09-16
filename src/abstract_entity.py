from abc import ABC, abstractmethod
from uuid import UUID, uuid4


class identify(ABC):
    """Абстрактный базовый класс для идентифицируемых сущностей."""
    __name = ""

    def __init__(self) -> None:
        """Инициализирует базовый экземпляр сущности."""
        self.__id = uuid4
    
    @property
    @abstractmethod
    def id(self) -> UUID:
        """Возвращает уникальный идентификатор сущности."""
        return self.__id

    @property
    @abstractmethod
    def name(self) -> str:
        """Возвращает наименование сущности."""
        return self.__name

    @name.setter
    @abstractmethod
    def name(self, value: str) -> None:
        """
        Устанавливает наименование сущности.

        :param value: Новое наименование сущности.
        """
        if self.__name is not None and len(self.__name) != 0:
            self.__name = value
