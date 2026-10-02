import math
from enum import Enum

from Src.Core.exception import ValidationException


class Validation:
    """Набор общих проверок значений для моделей."""

    @staticmethod
    def validate_instance[T](
        value: object,
        expected_type: type[T] | tuple[type[T], ...],
        field: str,
        message: str,
    ) -> T:
        """Проверяет, что значение — экземпляр одного из ожидаемых типов."""
        if not isinstance(value, expected_type):
            raise ValidationException(field, message)
        return value

    @staticmethod
    def validate_string(
        value: object,
        field: str,
        min_length: int = 1,
        max_length: int | None = None,
    ) -> str:
        """Проверяет строку по длине и возвращает её без пробелов по краям."""
        if not isinstance(value, str):
            raise ValidationException(field, "Ожидается строка")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValidationException(field, "Значение не должно быть пустым")
        if len(cleaned_value) < min_length:
            raise ValidationException(
                field, f"Длина должна быть не меньше {min_length} символов"
            )
        if max_length is not None and len(cleaned_value) > max_length:
            raise ValidationException(
                field, f"Длина не должна превышать {max_length} символов"
            )
        return cleaned_value

    @staticmethod
    def validate_positive_number(value: object, field: str) -> int | float:
        """Проверяет, что значение — конечное число строго больше нуля."""
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValidationException(field, "Ожидается число")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValidationException(field, "Значение должно быть конечным числом")
        if value <= 0:
            raise ValidationException(field, "Значение должно быть больше нуля")
        return value

    @staticmethod
    def validate_digits(
        value: object,
        field: str,
        min_length: int = 1,
        max_length: int | None = None,
    ) -> str:
        """Проверяет строку из ASCII-цифр заданной длины, возвращает её без пробелов."""
        cleaned_value = Validation.validate_string(
            value, field, min_length=min_length, max_length=max_length
        )
        if not (cleaned_value.isascii() and cleaned_value.isdigit()):
            raise ValidationException(field, "Ожидаются только цифры 0-9")
        return cleaned_value

    @staticmethod
    def validate_items(value: object, field: str) -> list[dict]:
        """Проверяет, что значение — список json-объектов, и возвращает его."""
        items = Validation.validate_instance(value, list, field, "Ожидается список")
        for item in items:
            Validation.validate_instance(
                item, dict, field, "Элемент списка должен быть объектом"
            )
        return items

    @staticmethod
    def validate_unique(key: str, collection: dict, field: str) -> str:
        """Проверяет, что ключа ещё нет в коллекции, и возвращает его."""
        if key in collection:
            raise ValidationException(field, f"Значение '{key}' указано повторно")
        return key

    @staticmethod
    def validate_reference[T](key: object, collection: dict[str, T], field: str) -> T:
        """Возвращает элемент коллекции, на который ссылается ключ."""
        if not isinstance(key, str) or key not in collection:
            raise ValidationException(field, f"Ссылка на неизвестный элемент '{key}'")
        return collection[key]

    @staticmethod
    def validate_enum[E: Enum](value: object, enum_type: type[E], field: str) -> E:
        """Возвращает элемент перечисления, соответствующий значению."""
        try:
            return enum_type(value)
        except ValueError as ex:
            raise ValidationException(
                field, "Значение не входит в допустимый набор"
            ) from ex
