from abc import ABC
from typing import Self
from uuid import UUID, uuid4


# Намеренно без абстрактных методов: класс — только маркер "не создавать напрямую".
class AbstractModel(ABC):  # noqa: B024
    """Абстрактный базовый класс для идентифицируемых сущностей."""

    def __init__(self) -> None:
        """Инициализирует базовый экземпляр сущности."""
        self.__id = str(uuid4())

    @property
    def id(self) -> UUID:
        """Возвращает уникальный идентификатор сущности."""
        return self.__id

    def __eq__(self, other: Self):
        """Сравнивает сущности по id."""
        return self.id == other.id
