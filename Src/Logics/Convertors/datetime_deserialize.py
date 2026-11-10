from datetime import datetime

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.exception import ValidationException
from Src.Core.validation import Validation


class DatetimeDeserialize(AbstractConvertor):
    """Конвертор строк ISO 8601 в даты по аннотациям полей модели."""

    def __init__(self, field_types: dict[str, object]) -> None:
        """Принимает ожидаемые типы полей модели."""
        self.__field_types = field_types

    def convert(self, source: object) -> dict:
        """Восстанавливает поля с ожидаемым типом datetime."""
        source = Validation.validate_instance(
            source, dict, "source", "Ожидается словарь модели"
        )
        result = {}
        for field, expected_type in self.__field_types.items():
            if field in source and expected_type is datetime:
                try:
                    result[field] = datetime.fromisoformat(source[field])
                except (TypeError, ValueError) as ex:
                    raise ValidationException(
                        field, "Ожидается дата в формате ISO 8601"
                    ) from ex
        return result
