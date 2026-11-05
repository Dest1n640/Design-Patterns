import inspect
from enum import Enum

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.exception import ValidationException
from Src.Core.validation import Validation


class EnumDeserialize(AbstractConvertor):
    """Конвертор значений JSON в перечисления по аннотациям полей модели."""

    def __init__(self, field_types: dict[str, object]) -> None:
        """Принимает ожидаемые типы полей модели."""
        self.__field_types = field_types

    def convert(self, source: object) -> dict:
        """Восстанавливает поля с ожидаемым типом Enum."""
        source = Validation.validate_instance(
            source, dict, "source", "Ожидается словарь модели"
        )
        result = {}
        for field, expected_type in self.__field_types.items():
            if (
                field in source
                and inspect.isclass(expected_type)
                and issubclass(expected_type, Enum)
            ):
                try:
                    result[field] = expected_type(source[field])
                except (TypeError, ValueError) as ex:
                    raise ValidationException(
                        field, f"Некорректное значение {expected_type.__name__}"
                    ) from ex
        return result
