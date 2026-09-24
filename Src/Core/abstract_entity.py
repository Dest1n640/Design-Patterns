from abc import ABC
from uuid import UUID, uuid4
from typing import Self

class abstract_model(ABC):
    """Абстрактный базовый класс для идентифицируемых сущностей."""

    def __init__(self) -> None:
        """Инициализирует базовый экземпляр сущности."""
        self.__id = str(uuid4())
    
    @property
    def id(self) -> UUID:
        """Возвращает уникальный идентификатор сущности."""
        return self.__id

    def __eq__(self, other: Self):
        """
        Магический метод сравнения

        :other: параметор сравнения
        """
        return self.id == other.id
