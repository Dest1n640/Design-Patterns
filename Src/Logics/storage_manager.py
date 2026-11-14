import json
from threading import RLock
from typing import Self

from Src.Core.abstract_manager import AbstractManager
from Src.Core.abstract_model import AbstractModel
from Src.Core.common import Common
from Src.Core.exception import (
    ApplicationException,
    ConflictException,
    NotFoundException,
    ValidationException,
)
from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation
from Src.Logics.deserialize_factory import DeserializeFactory
from Src.Logics.model_registry import ENTITY_TYPES
from Src.Logics.serialize_factory import SerializeFactory
from Src.Models.ingredient_model import IngredientModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.nomenclature_model import NomenclatureModel
from Src.Models.production_shop_model import ProductionShopModel
from Src.Models.restaurant_model import RestaurantModel
from Src.Models.settings_model import SettingsModel
from Src.Models.technological_map_model import TechnologicalMapModel
from Src.Models.warehouse_model import WarehouseModel


class StorageManager(AbstractManager):
    """Класс менеджера хранилища — singleton, хранит справочники доменных моделей."""

    _instance = None

    def __new__(cls) -> Self:
        """Возвращает единственный экземпляр менеджера хранилища."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Конструктор: состояние создаётся один раз для единственного экземпляра."""
        if hasattr(self, "_settings"):
            return
        super().__init__()
        self._lock = RLock()
        self._settings: SettingsModel | None = None
        self._collections: dict[str, dict[str, AbstractModel]] = {
            name: {} for name in ENTITY_TYPES
        }

    @property
    def settings(self) -> SettingsModel | None:
        """Возвращает настройки, с которыми запущено хранилище; None до запуска."""
        return self._settings

    @property
    def measurement_units(self) -> list[MeasurementUnitModel]:
        """Возвращает единицы измерения."""
        return self.get_entities("measurement_units")

    @property
    def nomenclature_groups(self) -> list[NomenclatureGroupModel]:
        """Возвращает группы номенклатуры."""
        return self.get_entities("nomenclature_groups")

    @property
    def nomenclature(self) -> list[NomenclatureModel]:
        """Возвращает номенклатуру."""
        return self.get_entities("nomenclature")

    @property
    def restaurants(self) -> list[RestaurantModel]:
        """Возвращает рестораны — владельцев складов."""
        return self.get_entities("restaurants")

    @property
    def production_shops(self) -> list[ProductionShopModel]:
        """Возвращает производственные цеха — владельцев складов."""
        return self.get_entities("production_shops")

    @property
    def warehouses(self) -> list[WarehouseModel]:
        """Возвращает склады."""
        return self.get_entities("warehouses")

    @property
    def technological_maps(self) -> list[TechnologicalMapModel]:
        """Возвращает технологические карты (рецепты)."""
        return self.get_entities("technological_maps")

    def get_entity_types(self) -> list[str]:
        """Возвращает имена зарегистрированных коллекций доменных сущностей."""
        return list(self._collections)

    def get_entities(self, entity_type: str) -> list[AbstractModel]:
        """Возвращает объекты указанной коллекции доменных сущностей."""
        with self._lock:
            return list(self._get_collection(entity_type).values())

    def get_entity(self, entity_type: str, entity_id: str) -> AbstractModel:
        """Возвращает сущность из указанной коллекции по идентификатору."""
        with self._lock:
            collection = self._get_collection(entity_type)
            try:
                return collection[entity_id]
            except KeyError as ex:
                raise NotFoundException(
                    f"Сущность '{entity_type}' с кодом '{entity_id}' не найдена"
                ) from ex

    def create_entity(self, entity_type: str, data: dict) -> AbstractModel:
        """Создаёт сущность и новые вложенные объекты после проверки всего запроса."""
        with self._lock:
            source = self._entity_source(entity_type, data)
            existing = self._all_models()
            factory = DeserializeFactory()
            model = factory.convert(source, existing)
            if any(entity.id == model.id for entity in existing):
                raise ConflictException("id", "Сущность с таким кодом уже существует")
            self._collections = self._merge_models(factory.models)
            return model

    def update_entity(
        self, entity_type: str, entity_id: str, data: dict
    ) -> AbstractModel:
        """Проверяет частичное изменение и применяет его с сохранением общих ссылок."""
        with self._lock:
            original = self.get_entity(entity_type, entity_id)
            changes = self._entity_source(entity_type, data)
            parameters = Common.get_constructor_parameters(type(original))
            for field in changes:
                if field not in parameters and field not in {"id", "type"}:
                    raise ValidationException(field, "Поле недоступно для изменения")
            serialized = SerializeFactory().convert(original)
            source = {
                field: value
                for field, value in serialized.items()
                if field in parameters or field == "id"
            } | changes
            existing = [model for model in self._all_models() if model is not original]
            factory = DeserializeFactory()
            updated = factory.convert(source, existing)
            id_changed = updated.id != original.id
            if id_changed:
                if any(model.id == updated.id for model in existing):
                    raise ConflictException("id", "Код уже занят другой сущностью")
                self._ensure_unreferenced(original)
            collections = self._merge_models(factory.models)
            if id_changed:
                del collections[entity_type][original.id]
            collections[entity_type][updated.id] = original
            original.replace_state(updated)
            self._collections = collections
            return original

    def delete_entity(self, entity_type: str, entity_id: str) -> None:
        """Удаляет сущность без входящих ссылок, сохраняя вложенные модели."""
        with self._lock:
            model = self.get_entity(entity_type, entity_id)
            self._ensure_unreferenced(model)
            del self._collections[entity_type][entity_id]

    def _entity_source(self, entity_type: str, data: dict) -> dict:
        """Проверяет коллекцию и тип входных данных, дополняя их меткой модели."""
        self._get_collection(entity_type)
        data = Validation.validate_instance(
            data, dict, "entity", "Сущность должна быть JSON-объектом"
        )
        type_name = ENTITY_TYPES[entity_type].__name__
        if data.get("type", type_name) != type_name:
            raise ValidationException("type", "Тип модели не соответствует коллекции")
        return data | {"type": type_name}

    def _all_models(self) -> list[AbstractModel]:
        """Возвращает объекты всех коллекций для проверки кодов и общих ссылок."""
        return [
            model
            for collection in self._collections.values()
            for model in collection.values()
        ]

    def _merge_models(
        self, models: list[AbstractModel]
    ) -> dict[str, dict[str, AbstractModel]]:
        """Собирает новые коллекции без изменения текущего состояния хранилища."""
        collections = {
            name: values.copy() for name, values in self._collections.items()
        }
        collection_names = {
            model_type: name for name, model_type in ENTITY_TYPES.items()
        }
        for model in models:
            if type(model) not in collection_names:
                raise ValidationException("type", "Ожидается доменная модель")
            collections[collection_names[type(model)]][model.id] = model
        return collections

    def _ensure_unreferenced(self, model: AbstractModel) -> None:
        """Запрещает удаление и смену кода при входящих ссылках на сущность."""
        owners = self._all_models()
        if self._settings is not None:
            owners.append(self._settings)
        for owner in owners:
            if owner is model:
                continue
            if any(
                self._references(getattr(owner, field), model.id)
                for field in Common.get_fields(owner)
            ):
                raise ConflictException(
                    "id", f"Сущность используется моделью '{type(owner).__name__}'"
                )

    @staticmethod
    def _references(value: object, entity_id: str) -> bool:
        """Проверяет наличие ссылки на код в свойстве или вложенной коллекции."""
        if isinstance(value, AbstractModel):
            return value.id == entity_id
        if isinstance(value, dict):
            value = list(value.values())
        if isinstance(value, list):
            return any(StorageManager._references(item, entity_id) for item in value)
        return False

    def _get_collection(self, entity_type: str) -> dict[str, AbstractModel]:
        """Возвращает коллекцию или сообщает об отсутствии её регистрации."""
        try:
            return self._collections[entity_type]
        except KeyError as ex:
            raise NotFoundException(f"Коллекция '{entity_type}' не найдена") from ex

    def start(self, settings: SettingsModel) -> None:
        """Запускает хранилище: при первом старте формирует первичные данные."""
        settings = Validation.validate_instance(
            settings, SettingsModel, "settings", "Настройки указаны некорректно"
        )
        # Повторный запуск не пересоздаёт уже сформированные данные.
        if self.is_loaded:
            return
        self._settings = settings
        if settings.first_start:
            self._is_loaded = self._create_default_data()

    def load(self) -> bool:
        """Восстанавливает справочники из загруженного JSON через DeserializeFactory."""
        data = Validation.validate_instance(
            self._data, dict, "storage", "Хранилище должно быть JSON-объектом"
        )
        if not any(field in data for field in ENTITY_TYPES):
            raise ValidationException("storage", "Отсутствуют коллекции хранилища")
        factory = DeserializeFactory()
        sources = {
            field: Validation.validate_instance(
                data.get(field, []), list, field, "Коллекция должна быть списком"
            )
            for field in ENTITY_TYPES
        }
        restored = factory.convert(sources)
        collections = {}
        entity_ids = set()
        for field, model_type in ENTITY_TYPES.items():
            models = restored[field]
            for model in models:
                if type(model) is not model_type:
                    raise ValidationException(
                        field, "Некорректный тип модели в коллекции"
                    )
                if model.id in entity_ids:
                    raise ValidationException(
                        "id", "Коды моделей не должны повторяться"
                    )
                entity_ids.add(model.id)
            collections[field] = {model.id: model for model in models}

        collection_names = {
            model_type: field for field, model_type in ENTITY_TYPES.items()
        }
        for model in factory.models:
            field = collection_names[type(model)]
            collections[field].setdefault(model.id, model)

        self._collections = collections
        return True

    def _create_default_data(self) -> bool:
        """Формирует первичные данные фабричными методами доменных моделей."""
        units = self._by_name(MeasurementUnitModel.create_default_units())
        groups = self._by_name(NomenclatureGroupModel.create_default_groups())
        nomenclature = NomenclatureModel.create_margherita_nomenclature(groups, units)
        restaurants = self._by_name(RestaurantModel.create_default_restaurants())
        production_shops = self._by_name(
            ProductionShopModel.create_default_production_shops()
        )
        warehouses = WarehouseModel.create_default_warehouses(
            restaurants, production_shops
        )
        technological_map = TechnologicalMapModel.create_technological_map(
            groups, units
        )
        defaults = {
            "measurement_units": list(units.values()),
            "nomenclature_groups": list(groups.values()),
            "nomenclature": nomenclature,
            "restaurants": list(restaurants.values()),
            "production_shops": list(production_shops.values()),
            "warehouses": warehouses,
            "technological_maps": [technological_map],
            "organizations": (
                [self._settings.organization] if self._settings.organization else []
            ),
            "premises": [warehouse.premises for warehouse in warehouses],
            "dishes": technological_map.dishes,
            "ingredients": [
                ingredient
                for dish in technological_map.dishes
                for ingredient in dish.ingredients
                if isinstance(ingredient, IngredientModel)
            ],
        }
        for field, models in defaults.items():
            self._collections[field] = {model.id: model for model in models}
        return True

    def save(self, file_name: str) -> None:
        """Выгружает все справочники хранилища в json-файл через SerializeFactory."""
        file_name = Validation.validate_string(file_name, "file_name")
        factory = SerializeFactory()
        data = {
            field: factory.convert(self.get_entities(field))
            for field in self.get_entity_types()
        }
        try:
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except OSError as ex:
            raise ApplicationException(
                f"Не удалось записать файл '{file_name}'"
            ) from ex

    @staticmethod
    def _by_name[T: NamedModel](models: list[T]) -> dict[str, T]:
        """Возвращает словарь моделей с ключом по имени."""
        return {model.name: model for model in models}
