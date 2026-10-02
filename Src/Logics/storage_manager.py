from typing import Self

from Src.Core.abstract_manager import AbstractManager
from Src.Core.exception import ValidationException
from Src.Core.position_type import PositionType
from Src.Core.validation import Validation
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.nomenclature_model import NomenclatureModel
from Src.Models.premises_model import PremisesModel
from Src.Models.production_shop_model import ProductionShopModel
from Src.Models.restaurant_model import RestaurantModel
from Src.Models.settings_model import SettingsModel
from Src.Models.warehouse_model import WarehouseModel


class StorageManager(AbstractManager):
    """Класс менеджера хранилища — singleton, хранит справочники доменных моделей."""

    _DEFAULT_FILE_NAME = "settings.json"
    _WAREHOUSE_TYPE_CENTRAL = "central"
    _WAREHOUSE_TYPE_RESTAURANT = "restaurant"
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

    def start(self, settings: SettingsModel, file_name: str = "") -> None:
        """Запускает хранилище: при первом старте формирует первичные данные."""
        settings = Validation.validate_instance(
            settings, SettingsModel, "settings", "Настройки указаны некорректно"
        )
        # Повторный запуск не пересоздаёт уже сформированные данные.
        if self.is_loaded:
            return
        self._settings = settings
        # Загрузка сохранённых данных — следующий этап, коллекции остаются пустыми.
        if not settings.first_start:
            return
        self.load(file_name)

    def convert(self) -> bool:
        """Формирует коллекции доменных моделей из секций загруженного файла."""
        data = Validation.validate_instance(
            self._data, dict, "storage", "Данные хранилища должны быть json-объектом"
        )
        workshop = Validation.validate_instance(
            data.get("production_workshop"),
            dict,
            "production_workshop",
            "Раздел production_workshop отсутствует или некорректен",
        )

        measurement_units = self._convert_measurement_units(
            data.get("measurement_units")
        )
        nomenclature_groups = self._convert_nomenclature_groups(
            data.get("nomenclature_groups")
        )
        nomenclature = self._convert_nomenclature(
            data.get("nomenclature"), nomenclature_groups, measurement_units
        )
        restaurants, restaurants_by_code = self._convert_restaurants(
            data.get("restaurants")
        )
        production_shop = ProductionShopModel(workshop.get("name"))
        warehouses = self._convert_warehouses(
            data.get("warehouses"), restaurants_by_code, production_shop
        )

        # Коллекции заменяются только после успешной обработки всех секций.
        self._measurement_units = measurement_units
        self._nomenclature_groups = nomenclature_groups
        self._nomenclature = nomenclature
        self._restaurants = restaurants
        self._production_shops = {production_shop.name: production_shop}
        self._warehouses = warehouses
        return True

    def _convert_measurement_units(
        self, items: object
    ) -> dict[str, MeasurementUnitModel]:
        """Создаёт единицы измерения, связывая их с базовыми по имени."""
        units: dict[str, MeasurementUnitModel] = {}
        for item in Validation.validate_items(items, "measurement_units"):
            # Базовая единица должна идти в файле раньше производной.
            base_unit_name = item.get("base_unit")
            base_unit = (
                None
                if base_unit_name is None
                else Validation.validate_reference(base_unit_name, units, "base_unit")
            )
            unit = MeasurementUnitModel(
                item.get("name"), item.get("coefficient"), base_unit
            )
            Validation.validate_unique(unit.name, units, "measurement_units")
            units[unit.name] = unit
        return units

    def _convert_nomenclature_groups(
        self, items: object
    ) -> dict[str, NomenclatureGroupModel]:
        """Создаёт группы номенклатуры."""
        groups: dict[str, NomenclatureGroupModel] = {}
        for item in Validation.validate_items(items, "nomenclature_groups"):
            group = NomenclatureGroupModel(item.get("name"))
            Validation.validate_unique(group.name, groups, "nomenclature_groups")
            groups[group.name] = group
        return groups

    def _convert_nomenclature(
        self,
        items: object,
        groups: dict[str, NomenclatureGroupModel],
        units: dict[str, MeasurementUnitModel],
    ) -> dict[str, NomenclatureModel]:
        """Создаёт номенклатуру, связывая её с группами и единицами измерения."""
        nomenclature: dict[str, NomenclatureModel] = {}
        for item in Validation.validate_items(items, "nomenclature"):
            position = NomenclatureModel(
                item.get("name"),
                item.get("full_name"),
                Validation.validate_reference(item.get("group"), groups, "group"),
                Validation.validate_reference(
                    item.get("measurement_unit"), units, "measurement_unit"
                ),
                Validation.validate_enum(
                    item.get("position_type"), PositionType, "position_type"
                ),
            )
            Validation.validate_unique(position.name, nomenclature, "nomenclature")
            nomenclature[position.name] = position
        return nomenclature

    def _convert_restaurants(
        self, items: object
    ) -> tuple[dict[str, RestaurantModel], dict[str, RestaurantModel]]:
        """Создаёт рестораны; возвращает их по имени и по коду из файла."""
        restaurants: dict[str, RestaurantModel] = {}
        restaurants_by_code: dict[str, RestaurantModel] = {}
        for item in Validation.validate_items(items, "restaurants"):
            restaurant = RestaurantModel(item.get("name"))
            code = Validation.validate_string(item.get("id"), "id")
            Validation.validate_unique(restaurant.name, restaurants, "restaurants")
            Validation.validate_unique(code, restaurants_by_code, "id")
            restaurants[restaurant.name] = restaurant
            restaurants_by_code[code] = restaurant
        return restaurants, restaurants_by_code

    def _convert_warehouses(
        self,
        items: object,
        restaurants_by_code: dict[str, RestaurantModel],
        production_shop: ProductionShopModel,
    ) -> dict[str, WarehouseModel]:
        """Создаёт склады с помещениями; владелец — ресторан по коду или цех."""
        warehouses: dict[str, WarehouseModel] = {}
        for item in Validation.validate_items(items, "warehouses"):
            premises_data = Validation.validate_instance(
                item.get("premises"),
                dict,
                "premises",
                "Помещение склада указано некорректно",
            )
            premises = PremisesModel(
                premises_data.get("name"),
                premises_data.get("address"),
                premises_data.get("square"),
            )

            warehouse_type = item.get("type")
            if warehouse_type == self._WAREHOUSE_TYPE_CENTRAL:
                owner = production_shop
            elif warehouse_type == self._WAREHOUSE_TYPE_RESTAURANT:
                owner = Validation.validate_reference(
                    item.get("restaurant_id"), restaurants_by_code, "restaurant_id"
                )
            else:
                raise ValidationException("type", "Тип склада указан некорректно")

            warehouse = WarehouseModel(item.get("name"), premises, owner)
            Validation.validate_unique(warehouse.name, warehouses, "warehouses")
            warehouses[warehouse.name] = warehouse
        return warehouses
