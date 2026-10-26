from abc import ABC
from typing import Self
from uuid import uuid4

from Src.Core.validation import Validation


# Намеренно без абстрактных методов: класс — только маркер "не создавать напрямую".
class AbstractModel(ABC):  # noqa: B024
    """Абстрактный базовый класс для идентифицируемых сущностей."""

    def __init__(self) -> None:
        """Инициализирует базовый экземпляр сущности."""
        self.__id = str(uuid4())

    @property
    def id(self) -> str:
        """Возвращает уникальный идентификатор сущности."""
        return self.__id

    @id.setter
    def id(self, new_id: str) -> None:
        """Устанавливает идентификатор — нужен при загрузке сущности из файла."""
        self.__id = Validation.validate_string(new_id, "id")

    def __eq__(self, other: Self):
        """Сравнивает сущности по id."""
        return self.id == other.id
