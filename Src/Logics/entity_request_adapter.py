from collections.abc import Callable

from Src.Core.abstract_model import AbstractModel
from Src.Core.common import Common
from Src.Core.exception import NotFoundException, ValidationException
from Src.Core.validation import Validation
from Src.Logics.deserialize_factory import DeserializeFactory
from Src.Logics.entity_type import EntityType
from Src.Logics.serialize_factory import SerializeFactory


class EntityRequestAdapter:
    """Преобразует JSON-запросы создания и частичного изменения в модели."""

    @staticmethod
    def create(
        entity_type: str,
        data: dict,
        find_model: Callable[[str], AbstractModel | None],
    ) -> AbstractModel:
        """Восстанавливает модель выбранной коллекции с общими вложенными объектами."""
        try:
            model_type = {item.name.lower(): item.value for item in EntityType}[
                entity_type
            ]
        except KeyError as ex:
            raise NotFoundException(f"Коллекция '{entity_type}' не найдена") from ex
        source = EntityRequestAdapter._source(model_type, data)
        return DeserializeFactory(find_model).convert(source)

    @staticmethod
    def update(
        original: AbstractModel,
        data: dict,
        find_model: Callable[[str], AbstractModel | None],
    ) -> AbstractModel:
        """Объединяет PATCH с текущими полями и восстанавливает проверенную модель."""
        changes = EntityRequestAdapter._source(type(original), data)
        field_types = Common.get_field_types(type(original))
        for field in changes:
            if field not in field_types and field != "type":
                raise ValidationException(field, "Поле недоступно для изменения")
        serialized = SerializeFactory().convert(original)
        source = {
            field: value for field, value in serialized.items() if field in field_types
        } | changes
        return DeserializeFactory(find_model, original).convert(source)

    @staticmethod
    def _source(model_type: type[AbstractModel], data: dict) -> dict:
        """Проверяет тело запроса и добавляет соответствующую коллекции метку типа."""
        data = Validation.validate_instance(
            data, dict, "entity", "Сущность должна быть JSON-объектом"
        )
        type_name = model_type.__name__
        if data.get("type", type_name) != type_name:
            raise ValidationException("type", "Тип модели не соответствует коллекции")
        return data | {"type": type_name}
