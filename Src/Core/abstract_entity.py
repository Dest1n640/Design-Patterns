from abc import ABC
from uuid import UUID, uuid4
from typing import Self
from Src.Core.exception import arguments_exception

class abstract_model(ABC):
    """Абстрактный базовый класс для идентифицируемых сущностей."""

    def __init__(self, name: str | None = None) -> None:
        """Инициализирует базовый экземпляр сущности."""
        self.__id = str(uuid4())
    
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

        :new_name : Новое наименование сущности.
        """
        if len(new_name) == 0 or new_name is None or not isinstance(new_name, str):
            raise arguments_exception("Name", "New_name is incorrect")
        self.__name = new_name

    def __eq__(self, other: Self):
        """
        Магический метод сравнения

        :other: параметор сравнения
        """
        return self.id == other.id
