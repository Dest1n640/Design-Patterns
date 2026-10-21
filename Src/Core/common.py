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
