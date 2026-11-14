import json
import os
from copy import copy
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock
from typing import Self

from Src.Core.abstract_manager import AbstractManager
from Src.Core.abstract_model import AbstractModel
from Src.Core.common import Common
from Src.Core.exception import (
    ConflictException,
    NotFoundException,
    PersistenceException,
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
    _DEFAULT_FILE_NAME = "tmp/storage.json"

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
        self._organization_id: str | None = None
        self._collections: dict[str, dict[str, AbstractModel]] = {
            name: {} for name in ENTITY_TYPES
        }

    def __enter__(self) -> Self:
        """Блокирует хранилище на время составной операции и сериализации."""
        self._lock.acquire()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Освобождает блокировку, включая выход из операции по исключению."""
        self._lock.release()

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
            self._commit_collections(self._merge_models(factory.models))
            return model

    def update_entity(
        self, entity_type: str, entity_id: str, data: dict
    ) -> AbstractModel:
        """Проверяет частичное изменение и применяет его с сохранением общих ссылок."""
        with self._lock:
            original = self.get_entity(entity_type, entity_id)
            changes = self._entity_source(entity_type, data)
            field_types = Common.get_field_types(type(original))
            for field in changes:
                if field not in field_types and field != "type":
                    raise ValidationException(field, "Поле недоступно для изменения")
            serialized = SerializeFactory().convert(original)
            source = {
                field: value
                for field, value in serialized.items()
                if field in field_types
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
            previous = copy(original)
            original.replace_state(updated)
            try:
                self._commit_collections(collections)
            except Exception:
                original.replace_state(previous)
                raise
            return original

    def delete_entity(self, entity_type: str, entity_id: str) -> None:
        """Удаляет сущность без входящих ссылок, сохраняя вложенные модели."""
        with self._lock:
            model = self.get_entity(entity_type, entity_id)
            self._ensure_unreferenced(model)
            collections = self._collections.copy()
            collections[entity_type] = collections[entity_type].copy()
            del collections[entity_type][entity_id]
            self._commit_collections(collections)

    def _commit_collections(
        self, collections: dict[str, dict[str, AbstractModel]]
    ) -> None:
        """Сохраняет изменения на диск перед заменой текущих коллекций."""
        if self._file_name:
            self._write_snapshot(self._file_name, collections)
        self._collections = collections

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
        if model.id == self._organization_id:
            raise ConflictException("id", "Организация используется настройками")
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

    def start(self, settings: SettingsModel, file_name: str = "") -> None:
        """Загружает сохранённые данные или создаёт и сохраняет начальное состояние."""
        settings = Validation.validate_instance(
            settings, SettingsModel, "settings", "Настройки указаны некорректно"
        )
        with self._lock:
            if self.is_loaded:
                if self._settings is None:
                    self._settings = settings
                    self._sync_organization()
                return
            if isinstance(file_name, str) and not file_name.strip():
                file_name = str(self._PROJECT_ROOT / self._DEFAULT_FILE_NAME)
            file_name = Validation.validate_string(file_name, "file_name")
            previous = (
                self._collections,
                self._settings,
                self._organization_id,
                self._file_name,
                self._is_loaded,
                self._data,
            )
            self._settings = settings
            try:
                if Path(file_name).exists():
                    self.read(file_name)
                    if self._data.get("organization_id") != self._organization_id:
                        self.save(file_name)
                else:
                    self._collections = (
                        self._create_default_data()
                        if settings.first_start
                        else {name: {} for name in ENTITY_TYPES}
                    )
                    self._organization_id = None
                    self._sync_organization()
                    self.save(file_name)
            except Exception:
                (
                    self._collections,
                    self._settings,
                    self._organization_id,
                    self._file_name,
                    self._is_loaded,
                    self._data,
                ) = previous
                raise

    def read(self, file_name: str = "") -> None:
        """Загружает файл под общей блокировкой и выбирает его для автосохранения."""
        with self._lock:
            super().read(file_name)
            self._file_name = str(Path(self._file_name).absolute())

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

        organization_id = data.get("organization_id")
        if organization_id is not None:
            organization_id = Validation.validate_string(
                organization_id, "organization_id"
            )
            if organization_id not in collections["organizations"]:
                raise ValidationException(
                    "organization_id", "Организация настроек отсутствует в хранилище"
                )
        self._collections = collections
        self._organization_id = organization_id
        self._sync_organization()
        return True

    def _sync_organization(self) -> None:
        """Связывает настройки с активной организацией из хранилища."""
        if self._settings is None:
            return
        organizations = self._collections["organizations"]
        if self._organization_id is None:
            if organizations:
                self._organization_id = next(iter(organizations))
            elif self._settings.organization is not None:
                organization = self._settings.organization
                organizations[organization.id] = organization
                self._organization_id = organization.id
        if self._organization_id is not None:
            self._settings.organization = organizations[self._organization_id]

    def _create_default_data(self) -> dict[str, dict[str, AbstractModel]]:
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
        collections = {name: {} for name in ENTITY_TYPES}
        for field, models in defaults.items():
            collections[field] = {model.id: model for model in models}
        return collections

    def save(self, file_name: str) -> None:
        """Атомарно сохраняет все коллекции и выбирает файл для автосохранения."""
        file_name = Validation.validate_string(file_name, "file_name")
        with self._lock:
            file_name = str(Path(file_name).absolute())
            self._write_snapshot(file_name, self._collections)
            self._file_name = file_name
            self._is_loaded = True

    def _write_snapshot(
        self, file_name: str, collections: dict[str, dict[str, AbstractModel]]
    ) -> None:
        """Записывает полный снимок во временный файл и атомарно заменяет целевой."""
        factory = SerializeFactory()
        data: dict[str, object] = {
            field: factory.convert(list(models.values()))
            for field, models in collections.items()
        }
        if self._organization_id is not None:
            data["organization_id"] = self._organization_id
        target = Path(file_name)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=target.parent,
                prefix=f".{target.name}.",
                delete_on_close=False,
            ) as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
                file.close()
                os.replace(file.name, target)
        except (OSError, ValueError, TypeError) as ex:
            raise PersistenceException(
                f"Не удалось записать файл '{file_name}'"
            ) from ex

    @staticmethod
    def _by_name[T: NamedModel](models: list[T]) -> dict[str, T]:
        """Возвращает словарь моделей с ключом по имени."""
        return {model.name: model for model in models}
