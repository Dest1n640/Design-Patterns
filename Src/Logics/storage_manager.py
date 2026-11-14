import json
from typing import Self

from Src.Core.abstract_manager import AbstractManager
from Src.Core.abstract_model import AbstractModel
from Src.Core.exception import (
    ApplicationException,
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
        return list(self._get_collection(entity_type).values())

    def get_entity(self, entity_type: str, entity_id: str) -> AbstractModel:
        """Возвращает сущность из указанной коллекции по идентификатору."""
        collection = self._get_collection(entity_type)
        try:
            return collection[entity_id]
        except KeyError as ex:
            raise NotFoundException(
                f"Сущность '{entity_type}' с кодом '{entity_id}' не найдена"
            ) from ex

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
        collections = {}
        entity_ids = set()
        for field, model_type in ENTITY_TYPES.items():
            source = Validation.validate_instance(
                data.get(field, []), list, field, "Коллекция должна быть списком"
            )
            models = factory.convert(source)
            for model in models:
                Validation.validate_instance(
                    model, model_type, field, "Некорректный тип модели в коллекции"
                )
                if model.id in entity_ids:
                    raise ValidationException(
                        "id", "Коды моделей не должны повторяться"
                    )
                entity_ids.add(model.id)
            collections[field] = {model.id: model for model in models}

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
