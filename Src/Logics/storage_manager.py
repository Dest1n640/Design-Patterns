from typing import Self

from Src.Core.abstract_manager import AbstractManager
from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation
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
        self._measurement_units: dict[str, MeasurementUnitModel] = {}
        self._nomenclature_groups: dict[str, NomenclatureGroupModel] = {}
        self._nomenclature: dict[str, NomenclatureModel] = {}
        self._restaurants: dict[str, RestaurantModel] = {}
        self._production_shops: dict[str, ProductionShopModel] = {}
        self._warehouses: dict[str, WarehouseModel] = {}
        self._technological_maps: dict[str, TechnologicalMapModel] = {}

    @property
    def settings(self) -> SettingsModel | None:
        """Возвращает настройки, с которыми запущено хранилище; None до запуска."""
        return self._settings

    @property
    def measurement_units(self) -> list[MeasurementUnitModel]:
        """Возвращает единицы измерения."""
        return list(self._measurement_units.values())

    @property
    def nomenclature_groups(self) -> list[NomenclatureGroupModel]:
        """Возвращает группы номенклатуры."""
        return list(self._nomenclature_groups.values())

    @property
    def nomenclature(self) -> list[NomenclatureModel]:
        """Возвращает номенклатуру."""
        return list(self._nomenclature.values())

    @property
    def restaurants(self) -> list[RestaurantModel]:
        """Возвращает рестораны — владельцев складов."""
        return list(self._restaurants.values())

    @property
    def production_shops(self) -> list[ProductionShopModel]:
        """Возвращает производственные цеха — владельцев складов."""
        return list(self._production_shops.values())

    @property
    def warehouses(self) -> list[WarehouseModel]:
        """Возвращает склады."""
        return list(self._warehouses.values())

    @property
    def technological_maps(self) -> list[TechnologicalMapModel]:
        """Возвращает технологические карты (рецепты)."""
        return list(self._technological_maps.values())

    def start(self, settings: SettingsModel) -> None:
        """Запускает хранилище: при первом старте формирует первичные данные."""
        settings = Validation.validate_instance(
            settings, SettingsModel, "settings", "Настройки указаны некорректно"
        )
        # Повторный запуск не пересоздаёт уже сформированные данные.
        if self.is_loaded:
            return
        self._settings = settings
        # Загрузка сохранённых данных — следующий этап, коллекции остаются пустыми.
        if settings.first_start:
            self._is_loaded = self.convert()

    def convert(self) -> bool:
        """Формирует первичные данные фабричными методами доменных моделей."""
        self._measurement_units = self._by_name(
            MeasurementUnitModel.create_default_units()
        )
        self._nomenclature_groups = self._by_name(
            NomenclatureGroupModel.create_default_groups()
        )
        self._nomenclature = self._by_name(
            NomenclatureModel.create_margherita_nomenclature(
                self._nomenclature_groups, self._measurement_units
            )
        )
        self._restaurants = self._by_name(RestaurantModel.create_default_restaurants())
        self._production_shops = self._by_name(
            ProductionShopModel.create_default_production_shops()
        )
        self._warehouses = self._by_name(
            WarehouseModel.create_default_warehouses(
                self._restaurants, self._production_shops
            )
        )
        self._technological_maps = self._by_name(
            [TechnologicalMapModel.create_technological_map()]
        )
        return True

    @staticmethod
    def _by_name[T: NamedModel](models: list[T]) -> dict[str, T]:
        """Возвращает словарь моделей с ключом по имени."""
        return {model.name: model for model in models}
