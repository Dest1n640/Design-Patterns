import inspect # интроспекция
from collections.abc import Mapping
from typing import get_args, get_origin, get_type_hints

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
    def get_collection_types(source: object) -> dict[str, type[AbstractModel]]:
        """Возвращает классы моделей коллекций по аннотациям публичных свойств."""
        result = {}
        for field in Common.get_fields(source):
            getter = getattr(type(source), field).fget
            field_type = get_type_hints(getter).get("return")
            item_types = get_args(field_type)
            if get_origin(field_type) is not list or not item_types:
                continue
            model_type = item_types[0]
            if inspect.isclass(model_type) and issubclass(model_type, AbstractModel):
                result[field] = model_type
        return result

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
