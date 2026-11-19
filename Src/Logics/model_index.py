from Src.Core.abstract_model import AbstractModel
from Src.Core.common import Common
from Src.Core.exception import ConflictException, ValidationException
from Src.Logics.entity_type import EntityType


class ModelIndex:
    """Регистрирует доменные модели и учитывает непосредственные входящие ссылки."""

    def __init__(self) -> None:
        """Создаёт пустые индексы для типов моделей из перечисления."""
        self._collection_names = {
            entity_type.value: entity_type.name.lower() for entity_type in EntityType
        }
        self.collections: dict[str, dict[str, AbstractModel]] = {
            name: {} for name in self._collection_names.values()
        }
        self.models: dict[str, AbstractModel] = {}
        self.reference_counts: dict[str, int] = {}
        self._visiting: set[str] = set()

    def register(self, model: AbstractModel) -> None:
        """Регистрирует модель и однократно обходит её сохраняемые свойства."""
        if type(model) not in self._collection_names:
            raise ValidationException("type", "Ожидается доменная модель")
        existing = self.models.get(model.id)
        if existing is not None and existing is not model:
            raise ConflictException(
                "id", f"Разные экземпляры модели с кодом '{model.id}'"
            )
        if model.id in self._visiting:
            raise ConflictException("id", "Циклические ссылки между моделями запрещены")
        if existing is not None:
            return
        self.models[model.id] = model
        self.collections[self._collection_names[type(model)]][model.id] = model
        self.reference_counts[model.id] = 0
        self._visiting.add(model.id)
        for reference in self.get_references(model):
            self.register_reference(reference)
        self._visiting.remove(model.id)

    def register_reference(self, value: object) -> None:
        """Учитывает ссылки в свойстве модели, списке или словаре."""
        for reference in self._nested_models(value):
            self.register(reference)
            self.reference_counts[reference.id] += 1

    def get_references(self, model: AbstractModel) -> list[AbstractModel]:
        """Возвращает непосредственные ссылки сохраняемых свойств модели."""
        return [
            reference
            for field in Common.get_field_types(type(model))
            for reference in self._nested_models(getattr(model, field))
        ]

    @staticmethod
    def _nested_models(value: object) -> list[AbstractModel]:
        """Извлекает модели из значения свойства без обхода их собственных полей."""
        if isinstance(value, AbstractModel):
            return [value]
        if isinstance(value, dict):
            value = list(value.values())
        if isinstance(value, list):
            return [
                model for item in value for model in ModelIndex._nested_models(item)
            ]
        return []

    def prepare_changes(
        self, models: list[AbstractModel], removed: list[AbstractModel]
    ) -> tuple[dict[str, AbstractModel], dict[str, int]]:
        """Проверяет изменения и вычисляет значения затронутых счётчиков."""
        removed_ids = {model.id for model in removed}
        if len(removed_ids) != len(removed):
            raise ConflictException(
                "id", "Коды удаляемых моделей не должны повторяться"
            )
        added = {}
        for model in models:
            if type(model) not in self._collection_names:
                raise ValidationException("type", "Ожидается доменная модель")
            if model.id in added or (
                model.id in self.models and model.id not in removed_ids
            ):
                raise ConflictException("id", "Код уже занят другой сущностью")
            added[model.id] = model

        differences = {}
        for model in removed:
            current = self.models.get(model.id)
            if type(current) is not type(model):
                raise ConflictException("id", "Удаляемая модель отсутствует в индексе")
            for reference in self.get_references(model):
                differences[reference.id] = differences.get(reference.id, 0) - 1
        for model in added.values():
            for reference in self.get_references(model):
                target = added.get(reference.id)
                if target is None and reference.id not in removed_ids:
                    target = self.models.get(reference.id)
                if target is not reference:
                    raise ConflictException(
                        "id", "Ссылка указывает на незарегистрированную модель"
                    )
                differences[reference.id] = differences.get(reference.id, 0) + 1

        counts = {
            entity_id: self.reference_counts.get(entity_id, 0) + difference
            for entity_id, difference in differences.items()
        }
        if any(count < 0 for count in counts.values()):
            raise ConflictException("id", "Некорректное изменение числа ссылок")
        for entity_id in removed_ids - added.keys():
            if counts.get(entity_id, self.reference_counts[entity_id]) != 0:
                raise ConflictException(
                    "id", "Удаляемая модель содержит входящие ссылки"
                )
        return added, counts

    def project_collections(
        self, added: dict[str, AbstractModel], removed: list[AbstractModel]
    ) -> dict[str, dict[str, AbstractModel]]:
        """Готовит коллекции для записи, копируя только изменяемые справочники."""
        collections = self.collections.copy()
        for model in [*removed, *added.values()]:
            field = self._collection_names[type(model)]
            if collections[field] is self.collections[field]:
                collections[field] = self.collections[field].copy()
        for model in removed:
            replacement = added.get(model.id)
            if type(replacement) is not type(model):
                del collections[self._collection_names[type(model)]][model.id]
        for model in added.values():
            collections[self._collection_names[type(model)]][model.id] = model
        return collections

    def apply_changes(
        self,
        added: dict[str, AbstractModel],
        removed: list[AbstractModel],
        counts: dict[str, int],
    ) -> None:
        """Применяет подготовленные изменения моделей и счётчиков после сохранения."""
        for model in removed:
            replacement = added.get(model.id)
            if type(replacement) is not type(model):
                del self.collections[self._collection_names[type(model)]][model.id]
            if model.id not in added:
                del self.models[model.id]
                del self.reference_counts[model.id]
        for model in added.values():
            self.models[model.id] = model
            self.collections[self._collection_names[type(model)]][model.id] = model
            self.reference_counts.setdefault(model.id, 0)
        for entity_id, count in counts.items():
            if entity_id in self.models:
                self.reference_counts[entity_id] = count
