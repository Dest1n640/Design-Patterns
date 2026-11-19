import inspect  # интроспекция
from typing import get_type_hints

from Src.Core.exception import ValidationException


class Common:
    """Набор общих статических методов."""

    @staticmethod
    def get_fields(source: object, is_common: bool = False) -> list[str]:
        """Возвращает публичные свойства модели; is_common — без списков и словарей."""
        if source is None:
            raise ValidationException("source", "Источник не указан")
        fields = []
        for name in dir(source):
            attribute = getattr(type(source), name, None)
            if name.startswith("_") or not isinstance(attribute, property):
                continue
            if is_common and isinstance(getattr(source, name), list | dict):
                continue
            fields.append(name)
        return fields

    @staticmethod
    def get_field_types(source: type) -> dict[str, object]:
        """Возвращает типы публичных свойств класса с сеттерами."""
        if not inspect.isclass(source):
            raise ValidationException(
                "source", "Ожидается класс для получения типов свойств"
            )
        field_types = {}
        for name, attribute in inspect.getmembers(source):
            if (
                name.startswith("_")
                or not isinstance(attribute, property)
                or attribute.fset is None
            ):
                continue
            setter_hints = get_type_hints(attribute.fset)
            setter_hints.pop("self", None)
            setter_hints.pop("return", None)
            field_types[name] = next(iter(setter_hints.values()), object)
        return field_types
