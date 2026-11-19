import json
import os
from contextlib import suppress
from pathlib import Path
from threading import RLock
from typing import Self
from uuid import uuid4

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
from Src.Logics.entity_type import EntityType
from Src.Logics.model_index import ModelIndex
from Src.Logics.serialize_factory import SerializeFactory
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.nomenclature_model import NomenclatureModel
from Src.Models.production_shop_model import ProductionShopModel
from Src.Models.restaurant_model import RestaurantModel
from Src.Models.settings_model import SettingsModel
from Src.Models.technological_map_model import TechnologicalMapModel
from Src.Models.warehouse_model import WarehouseModel


class StorageManager(AbstractManager):
    """Хранит справочники; зарегистрированные модели изменяет EntityService."""

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
        self._index = ModelIndex()

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
    def organization_id(self) -> str | None:
        """Возвращает код организации, выбранной при загрузке хранилища."""
        return self._organization_id

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
        return list(self._index.collections)

    def get_entities(self, entity_type: str) -> list[AbstractModel]:
        """Возвращает сохранённые модели коллекции для чтения."""
        with self._lock:
            return list(self._get_collection(entity_type).values())

    def get_entity(self, entity_type: str, entity_id: str) -> AbstractModel:
        """Возвращает сохранённую модель по идентификатору для чтения."""
        with self._lock:
            collection = self._get_collection(entity_type)
            try:
                return collection[entity_id]
            except KeyError as ex:
                raise NotFoundException(
                    f"Сущность '{entity_type}' с кодом '{entity_id}' не найдена"
                ) from ex

    def get_all_models(self) -> list[AbstractModel]:
        """Возвращает сохранённые модели всех коллекций для чтения."""
        with self._lock:
            return list(self._index.models.values())

    def find_model(self, entity_id: str) -> AbstractModel | None:
        """Находит сохранённую модель для чтения или возвращает None."""
        with self._lock:
            return self._index.models.get(entity_id)

    def get_reference_count(self, entity_id: str) -> int:
        """Возвращает число непосредственных входящих ссылок на модель."""
        with self._lock:
            if entity_id not in self._index.models:
                raise NotFoundException(f"Сущность с кодом '{entity_id}' не найдена")
            return self._index.reference_counts[entity_id]

    def commit(self, models: list[AbstractModel]) -> None:
        """Атомарно сохраняет набор моделей перед заменой индексов хранилища."""
        with self._lock:
            index, organization_id = self._build_indexes(models, self._organization_id)
            if self._file_name:
                self._write_snapshot(self._file_name, index.collections)
            self._index = index
            self._organization_id = organization_id

    def apply_changes(
        self, models: list[AbstractModel], removed: list[AbstractModel]
    ) -> None:
        """Сохраняет проверенные изменения перед обновлением затронутых индексов."""
        with self._lock:
            added, counts = self._index.prepare_changes(models, removed)
            if self._file_name:
                collections = self._index.project_collections(added, removed)
                self._write_snapshot(self._file_name, collections)
            self._index.apply_changes(added, removed, counts)

    def _build_indexes(
        self,
        models: list[AbstractModel],
        organization_id: str | None,
        synchronize_settings: bool = False,
    ) -> tuple[ModelIndex, str | None]:
        """Регистрирует граф моделей и строит независимый снимок индексов и ссылок."""
        index = ModelIndex()
        root_ids = set()
        for model in models:
            if not isinstance(model, AbstractModel):
                raise ValidationException("type", "Ожидается доменная модель")
            if model.id in root_ids:
                raise ConflictException("id", "Коды моделей не должны повторяться")
            root_ids.add(model.id)
            index.register(model)

        if (
            organization_id is not None
            and organization_id not in index.collections["organizations"]
        ):
            raise ValidationException(
                "organization_id", "Организация настроек отсутствует в хранилище"
            )
        if self._settings is not None:
            settings = self._settings.clone()
            if synchronize_settings:
                organizations = index.collections["organizations"]
                organization = (
                    organizations[organization_id]
                    if organization_id is not None
                    else next(iter(organizations.values()), settings.organization)
                )
                if organization is not None:
                    settings.organization = organization
                    organization_id = organization.id
            for field in Common.get_field_types(type(settings)):
                index.register_reference(getattr(settings, field))
        elif organization_id is not None:
            index.register_reference(
                index.collections["organizations"][organization_id]
            )
        return index, organization_id

    def _get_collection(self, entity_type: str) -> dict[str, AbstractModel]:
        """Возвращает коллекцию или сообщает об отсутствии её регистрации."""
        try:
            return self._index.collections[entity_type]
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
                    try:
                        indexes = self._build_indexes(
                            self.get_all_models(), self._organization_id, True
                        )
                    except Exception:
                        self._settings = None
                        raise
                    self._index, self._organization_id = indexes
                    self._sync_organization()
                return
            if isinstance(file_name, str) and not file_name.strip():
                file_name = str(self._PROJECT_ROOT / self._DEFAULT_FILE_NAME)
            file_name = Validation.validate_string(file_name, "file_name")
            previous = (
                self._index,
                self._settings,
                self._organization_id,
                self._file_name,
                self._is_loaded,
                self._data,
            )
            previous_settings = settings.clone()
            self._settings = settings
            try:
                if Path(file_name).exists():
                    self.read(file_name)
                    if self._data.get("organization_id") != self._organization_id:
                        self.save(file_name)
                else:
                    models = self._create_default_data() if settings.first_start else []
                    self._index, self._organization_id = self._build_indexes(
                        models, None, True
                    )
                    self._sync_organization()
                    self.save(file_name)
            except Exception:
                (
                    self._index,
                    self._settings,
                    self._organization_id,
                    self._file_name,
                    self._is_loaded,
                    self._data,
                ) = previous
                settings.replace_state(previous_settings)
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
        collection_names = self.get_entity_types()
        unknown_keys = data.keys() - set(collection_names) - {"organization_id"}
        if unknown_keys:
            names = ", ".join(sorted(unknown_keys))
            raise ValidationException("storage", f"Неизвестные ключи: {names}")
        if not any(name in data for name in collection_names):
            raise ValidationException("storage", "Отсутствуют коллекции хранилища")
        factory = DeserializeFactory()
        sources = {
            name: Validation.validate_instance(
                data.get(name, []),
                list,
                name,
                "Коллекция должна быть списком",
            )
            for name in collection_names
        }
        restored = factory.convert(sources)
        roots = []
        for entity_type in EntityType:
            field = entity_type.name.lower()
            models = restored[field]
            for model in models:
                if type(model) is not entity_type.value:
                    raise ValidationException(
                        field, "Некорректный тип модели в коллекции"
                    )
            roots.extend(models)

        organization_id = data.get("organization_id")
        if organization_id is not None:
            organization_id = Validation.validate_string(
                organization_id, "organization_id"
            )
        self._index, self._organization_id = self._build_indexes(
            roots, organization_id, True
        )
        self._sync_organization()
        return True

    def _sync_organization(self) -> None:
        """Связывает настройки с активной организацией из хранилища."""
        if self._settings is not None and self._organization_id is not None:
            self._settings.organization = self._index.models[self._organization_id]

    def _create_default_data(self) -> list[AbstractModel]:
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
        return [
            *units.values(),
            *groups.values(),
            *nomenclature,
            *restaurants.values(),
            *production_shops.values(),
            *warehouses,
            technological_map,
        ]

    def save(self, file_name: str) -> None:
        """Атомарно сохраняет все коллекции и выбирает файл для автосохранения."""
        file_name = Validation.validate_string(file_name, "file_name")
        with self._lock:
            file_name = str(Path(file_name).absolute())
            self._write_snapshot(file_name, self._index.collections)
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
        temporary = target.with_name(f".{target.name}.{uuid4()}.tmp")
        created = False
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with temporary.open("x", encoding="utf-8") as file:
                created = True
                json.dump(data, file, ensure_ascii=False, indent=2, allow_nan=False)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, target)
        except (OSError, ValueError, TypeError) as ex:
            if created:
                with suppress(OSError):
                    temporary.unlink(missing_ok=True)
            raise PersistenceException(
                f"Не удалось записать файл '{file_name}'"
            ) from ex

    @staticmethod
    def _by_name[T: NamedModel](models: list[T]) -> dict[str, T]:
        """Возвращает словарь моделей с ключом по имени."""
        return {model.name: model for model in models}
