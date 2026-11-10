from abc import ABC, abstractmethod


class AbstractConvertor(ABC):
    """Общий интерфейс сериализации и десериализации данных."""

    @abstractmethod
    def convert(self, source: object) -> object:
        """Преобразует исходные данные в целевое представление."""
