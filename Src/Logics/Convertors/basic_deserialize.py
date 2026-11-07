from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.validation import Validation


class BasicDeserialize(AbstractConvertor):
    """Конвертор простых значений полей из словаря JSON."""

    def convert(self, source: object) -> dict:
        """Возвращает числовые, строковые и пустые значения полей."""
        source = Validation.validate_instance(
            source, dict, "source", "Ожидается словарь модели"
        )
        return {
            field: value
            for field, value in source.items()
            if value is None or isinstance(value, str | int | float)
        }
