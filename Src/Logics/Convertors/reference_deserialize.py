from collections.abc import Callable

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.validation import Validation


class ReferenceDeserialize(AbstractConvertor):
    """Конвертор вложенных описаний моделей из словаря JSON."""

    def __init__(self, convert: Callable[[object], object]) -> None:
        """Принимает метод фабрики для восстановления вложенных моделей."""
        self.__convert = convert

    def convert(self, source: object) -> dict:
        """Восстанавливает свойства-модели, содержащие метку type."""
        source = Validation.validate_instance(
            source, dict, "source", "Ожидается словарь модели"
        )
        return {
            field: self.__convert(value)
            for field, value in source.items()
            if isinstance(value, dict) and "type" in value
        }
