from collections.abc import Callable

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.validation import Validation


class CollectionDeserialize(AbstractConvertor):
    """Конвертор списков, обычных словарей и свойств-коллекций из JSON."""

    def __init__(self, convert: Callable[[object], object]) -> None:
        """Принимает метод фабрики для восстановления элементов коллекции."""
        self.__convert = convert

    def convert(self, source: object) -> dict | list:
        """Рекурсивно восстанавливает коллекцию или собирает коллекции модели."""
        source = Validation.validate_instance(
            source, (list, dict), "source", "Ожидается список или словарь"
        )
        if isinstance(source, list):
            return [self.__convert(item) for item in source]
        if "type" not in source:
            return {key: self.__convert(value) for key, value in source.items()}
        return {
            field: self.__convert(value)
            for field, value in source.items()
            if isinstance(value, list)
            or isinstance(value, dict)
            and "type" not in value
        }
