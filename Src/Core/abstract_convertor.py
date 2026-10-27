from abc import ABC, abstractmethod


class AbstractConvertor(ABC):
    """Конвертор: превращает объект в словарь «наименование поля → данные поля»."""

    @abstractmethod
    def convert(self, source: object) -> dict:
        """Преобразует объект в словарь."""
