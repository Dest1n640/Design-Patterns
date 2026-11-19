from Src.Core.abstract_model import AbstractModel
from Src.Core.common import Common
from Src.Core.exception import ConflictException, ValidationException
from Src.Logics.entity_type import EntityType
from Src.Logics.storage_manager import StorageManager


class EntityService:
    """Выполняет операции над моделями с проверкой связей и сохранением изменений."""

    def __init__(self, storage: StorageManager) -> None:
        """Принимает хранилище моделей для выполнения операций."""
        self._storage = storage

    def create(self, model: AbstractModel) -> AbstractModel:
        """Создаёт модель и вложенные объекты с едиными экземплярами по коду."""
        with self._storage:
            self._validate_model(model)
            models = {}
            if self._storage.find_model(model.id) is not None:
                raise ConflictException("id", "Сущность с таким кодом уже существует")
            created = self._resolve(model, models, {}, set())
            self._storage.apply_changes(list(models.values()), [])
            return created

    def update(
        self, entity_type: str, entity_id: str, replacement: AbstractModel
    ) -> AbstractModel:
        """Применяет проверенное состояние, сохраняя общие ссылки и откат при ошибке."""
        with self._storage:
            original = self._storage.get_entity(entity_type, entity_id)
            if type(replacement) is not type(original):
                raise ValidationException(
                    "type", "Тип модели не соответствует коллекции"
                )
            models = {}
            if replacement.id != original.id:
                if self._storage.find_model(replacement.id) is not None:
                    raise ConflictException("id", "Код уже занят другой сущностью")
                self._ensure_unreferenced(original)
            updated = self._resolve(replacement, models, {}, set(), original)
            previous = original.clone()
            original.replace_state(updated)
            models[original.id] = original
            try:
                self._storage.apply_changes(list(models.values()), [previous])
            except Exception:
                original.replace_state(previous)
                raise
            return original

    def delete(self, entity_type: str, entity_id: str) -> None:
        """Удаляет модель без входящих ссылок, сохраняя её вложенные объекты."""
        with self._storage:
            model = self._storage.get_entity(entity_type, entity_id)
            self._ensure_unreferenced(model)
            self._storage.apply_changes([], [model])

    def _resolve(
        self,
        value: object,
        models: dict[str, AbstractModel],
        memo: dict[int, AbstractModel],
        visiting: set[int],
        excluded_model: AbstractModel | None = None,
    ) -> object:
        """Собирает граф с общими экземплярами, сохраняя исходные объекты."""
        if isinstance(value, list):
            return [
                self._resolve(item, models, memo, visiting, excluded_model)
                for item in value
            ]
        if isinstance(value, dict):
            return {
                key: self._resolve(item, models, memo, visiting, excluded_model)
                for key, item in value.items()
            }
        if not isinstance(value, AbstractModel):
            return value
        self._validate_model(value)
        if id(value) in visiting:
            raise ConflictException("id", "Циклические ссылки между моделями запрещены")
        if id(value) in memo:
            return memo[id(value)]
        visiting.add(id(value))
        fields = {
            field: self._resolve(
                getattr(value, field), models, memo, visiting, excluded_model
            )
            for field in Common.get_field_types(type(value))
        }
        visiting.remove(id(value))
        existing = models.get(value.id)
        if existing is None:
            existing = self._storage.find_model(value.id)
            if existing is excluded_model:
                existing = None
        if existing is not None:
            if type(existing) is not type(value) or any(
                not self._same_value(getattr(existing, field), getattr(value, field))
                for field in fields
            ):
                raise ConflictException(
                    "id", f"Противоречивые данные модели с кодом '{value.id}'"
                )
            memo[id(value)] = existing
            return existing
        model = value.clone()
        for field, resolved in fields.items():
            setattr(model, field, resolved)
        model.validate()
        models[model.id] = model
        memo[id(value)] = model
        return model

    @staticmethod
    def _same_value(first: object, second: object) -> bool:
        """Сравнивает значения полей с учётом классов и кодов вложенных моделей."""
        if isinstance(first, AbstractModel) or isinstance(second, AbstractModel):
            return type(first) is type(second) and first.id == second.id
        if isinstance(first, list) and isinstance(second, list):
            return len(first) == len(second) and all(
                EntityService._same_value(value, second[index])
                for index, value in enumerate(first)
            )
        if isinstance(first, dict) and isinstance(second, dict):
            return first.keys() == second.keys() and all(
                EntityService._same_value(value, second[key])
                for key, value in first.items()
            )
        return first == second

    @staticmethod
    def _validate_model(model: AbstractModel) -> None:
        """Проверяет принадлежность объекта к зарегистрированным доменным моделям."""
        if type(model) not in (entity_type.value for entity_type in EntityType):
            raise ValidationException("type", "Ожидается доменная модель")

    def _ensure_unreferenced(self, model: AbstractModel) -> None:
        """Запрещает удаление и смену кода модели при наличии входящих ссылок."""
        if self._storage.get_reference_count(model.id) > 0:
            raise ConflictException(
                "id", "Сущность используется другими моделями или настройками"
            )
