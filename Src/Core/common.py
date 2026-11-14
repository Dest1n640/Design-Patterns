import inspect  # интроспекция
from collections.abc import Mapping

from Src.Core.abstract_model import AbstractModel
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
    def get_constructor_parameters(
        source: type[AbstractModel],
    ) -> Mapping[str, inspect.Parameter]:
        """Возвращает параметры конструктора класса модели."""
        if not inspect.isclass(source) or not issubclass(source, AbstractModel):
            raise ValidationException(
                "source", "Ожидается класс, унаследованный от AbstractModel"
            )
        signature = inspect.signature(source)
        return signature.parameters
