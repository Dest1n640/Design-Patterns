import inspect
from typing import get_type_hints

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.common import Common
from Src.Core.exception import ValidationException
from Src.Logics.Convertors.basic_deserialize import BasicDeserialize
from Src.Logics.Convertors.collection_deserialize import CollectionDeserialize
from Src.Logics.Convertors.datetime_deserialize import DatetimeDeserialize
from Src.Logics.Convertors.enum_deserialize import EnumDeserialize
from Src.Logics.Convertors.reference_deserialize import ReferenceDeserialize
from Src.Logics.model_registry import ENTITY_TYPES
from Src.Models.settings_model import SettingsModel


class DeserializeFactory(AbstractConvertor):
    """Фабрика восстановления моделей из словарей и списков JSON."""

    def __init__(self) -> None:
        """Получает доменные типы из реестра и добавляет модель настроек."""
        self.__model_types = {
            model_type.__name__: model_type for model_type in ENTITY_TYPES.values()
        }
        self.__model_types[SettingsModel.__name__] = SettingsModel

    def convert(self, source: object) -> object:
        """Рекурсивно восстанавливает модели и сохраняет их идентификаторы."""
        if isinstance(source, list):
            return CollectionDeserialize(self.convert).convert(source)
        if not isinstance(source, dict):
            if source is None or isinstance(source, str | int | float):
                return source
            raise ValidationException("source", "Ожидаются данные из JSON")
        if "type" not in source:
            return CollectionDeserialize(self.convert).convert(source)

        type_name = source.get("type")
        if not isinstance(type_name, str) or type_name not in self.__model_types:
            raise ValidationException("type", "Неизвестный тип модели")
        model_class = self.__model_types[type_name]
        parameters = Common.get_constructor_parameters(model_class)
        field_types = get_type_hints(model_class.__init__)
        convertors: list[AbstractConvertor] = [
            BasicDeserialize(),
            DatetimeDeserialize(field_types),
            EnumDeserialize(field_types),
            ReferenceDeserialize(self.convert),
            CollectionDeserialize(self.convert),
        ]
        fields = {}
        for convertor in convertors:
            fields.update(convertor.convert(source))

        arguments = {}
        for key, item in parameters.items():
            if key in source:
                if key not in fields:
                    raise ValidationException(key, "Ожидаются данные из JSON")
                arguments[key] = fields[key]
            elif item.default is inspect.Parameter.empty:
                raise ValidationException(key, "Отсутствует обязательный параметр")

        model = model_class(**arguments)
        if "id" in source:
            model.id = source["id"]
        return model
