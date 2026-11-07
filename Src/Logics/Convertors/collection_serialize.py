from collections.abc import Callable

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.common import Common


class CollectionSerialize(AbstractConvertor):
    """Конвертор списков, словарей и свойств-коллекций модели в данные JSON."""

    def __init__(self, convert: Callable[[object], object]) -> None:
        """Принимает метод фабрики для сериализации элементов коллекции."""
        self.__convert = convert

    def convert(self, source: object) -> dict | list:
        """Рекурсивно сериализует коллекцию или собирает коллекции модели."""
        if isinstance(source, list):
            return [self.__convert(item) for item in source]
        if isinstance(source, dict):
            return {key: self.__convert(value) for key, value in source.items()}
        return {
            field: self.convert(getattr(source, field))
            for field in Common.get_fields(source)
            if isinstance(getattr(source, field), list | dict)
        }
