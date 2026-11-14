import inspect
from functools import partial
from typing import get_type_hints

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.abstract_model import AbstractModel
from Src.Core.common import Common
from Src.Core.exception import ConflictException, ValidationException
from Src.Logics.Convertors.basic_deserialize import BasicDeserialize
from Src.Logics.Convertors.collection_deserialize import CollectionDeserialize
from Src.Logics.Convertors.datetime_deserialize import DatetimeDeserialize
from Src.Logics.Convertors.enum_deserialize import EnumDeserialize
from Src.Logics.Convertors.reference_deserialize import ReferenceDeserialize
from Src.Logics.model_registry import ENTITY_TYPES
from Src.Logics.serialize_factory import SerializeFactory
from Src.Models.settings_model import SettingsModel


class DeserializeFactory(AbstractConvertor):
    """Фабрика восстановления моделей из словарей и списков JSON."""

    def __init__(self) -> None:
        """Получает доменные типы из реестра и добавляет модель настроек."""
        self.__model_types = {
            model_type.__name__: model_type for model_type in ENTITY_TYPES.values()
        }
        self.__model_types[SettingsModel.__name__] = SettingsModel
        self.__models: dict[str, AbstractModel] = {}

    @property
    def models(self) -> list[AbstractModel]:
        """Возвращает уникальные модели последней успешной десериализации."""
        return list(self.__models.values())

    def convert(
        self,
        source: object,
        existing_models: list[AbstractModel] | None = None,
    ) -> object:
        """Восстанавливает граф с единым экземпляром каждой модели по id."""
        models = {model.id: model for model in existing_models or []}
        result = self._convert(source, models)
        self.__models = models
        return result

    def _convert(self, source: object, models: dict[str, AbstractModel]) -> object:
        """Рекурсивно восстанавливает данные в пределах одного графа моделей."""
        convert = partial(self._convert, models=models)
        if isinstance(source, list):
            return CollectionDeserialize(convert).convert(source)
        if not isinstance(source, dict):
            if source is None or isinstance(source, str | int | float):
                return source
            raise ValidationException("source", "Ожидаются данные из JSON")
        if "type" not in source:
            return CollectionDeserialize(convert).convert(source)

        type_name = source.get("type")
        if not isinstance(type_name, str) or type_name not in self.__model_types:
            raise ValidationException("type", "Неизвестный тип модели")
        model_class = self.__model_types[type_name]
        parameters = Common.get_constructor_parameters(model_class)
        field_types = get_type_hints(model_class.__init__)
        model_data = {
            key: value
            for key, value in source.items()
            if key == "type" or key in parameters
        }
        convertors: list[AbstractConvertor] = [
            BasicDeserialize(),
            DatetimeDeserialize(field_types),
            EnumDeserialize(field_types),
            ReferenceDeserialize(convert),
            CollectionDeserialize(convert),
        ]
        fields = {}
        for convertor in convertors:
            fields.update(convertor.convert(model_data))

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
        existing = models.get(model.id)
        if existing is not None:
            serializer = SerializeFactory()
            if type(existing) is not model_class or (
                serializer.convert(existing) != serializer.convert(model)
            ):
                raise ConflictException(
                    "id", f"Противоречивые данные модели с кодом '{model.id}'"
                )
            return existing
        models[model.id] = model
        return model
