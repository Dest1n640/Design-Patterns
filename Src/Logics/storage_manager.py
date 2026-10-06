from typing import Self

from Src.Core.abstract_manager import AbstractManager
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
        """Формирует первичные данные: справочники доменных моделей."""
        self._measurement_units = self._create_measurement_units()
        self._nomenclature_groups = self._create_nomenclature_groups()
        self._nomenclature = self._create_nomenclature(
            self._nomenclature_groups, self._measurement_units
        )
        self._restaurants = self._create_restaurants()
        self._production_shops = self._create_production_shops()
        self._warehouses = self._create_warehouses(
            self._restaurants, self._production_shops
        )
        return True

    @staticmethod
    def _create_measurement_units() -> dict[str, MeasurementUnitModel]:
        """Создаёт базовые единицы измерения и кратные им."""
        gram = MeasurementUnitModel.create_gram()
        milliliter = MeasurementUnitModel.create_milliliter()
        kilogram = MeasurementUnitModel.create_kilogram(gram)
        liter = MeasurementUnitModel.create_liter(milliliter)
        piece = MeasurementUnitModel.create_piece()
        units = [gram, kilogram, milliliter, liter, piece]
        return {unit.name: unit for unit in units}

    @staticmethod
    def _create_nomenclature_groups() -> dict[str, NomenclatureGroupModel]:
        """Создаёт группы номенклатуры."""
        names = ["Бакалея", "Молочные продукты", "Овощи", "Полуфабрикаты", "Блюда"]
        return {name: NomenclatureGroupModel(name) for name in names}

    @staticmethod
    def _create_nomenclature(
        groups: dict[str, NomenclatureGroupModel],
        units: dict[str, MeasurementUnitModel],
    ) -> dict[str, NomenclatureModel]:
        """Создаёт номенклатуру рецепта пиццы Маргарита: сырьё, тесто и блюдо."""
        positions = [
            NomenclatureModel(
                "Мука пшеничная",
                "Мука пшеничная высшего сорта",
                groups["Бакалея"],
                units["килограмм"],
                PositionType.RAW_MATERIAL,
            ),
            NomenclatureModel(
                "Дрожжи сухие",
                "Дрожжи хлебопекарные сухие",
                groups["Бакалея"],
                units["грамм"],
                PositionType.RAW_MATERIAL,
            ),
            NomenclatureModel(
                "Соль",
                "Соль поваренная пищевая",
                groups["Бакалея"],
                units["грамм"],
                PositionType.RAW_MATERIAL,
            ),
            NomenclatureModel(
                "Масло оливковое",
                "Масло оливковое Extra Virgin",
                groups["Бакалея"],
                units["миллилитр"],
                PositionType.RAW_MATERIAL,
            ),
            NomenclatureModel(
                "Сыр Моцарелла",
                "Сыр Моцарелла для пиццы 45%",
                groups["Молочные продукты"],
                units["килограмм"],
                PositionType.RAW_MATERIAL,
            ),
            NomenclatureModel(
                "Томаты",
                "Томаты свежие",
                groups["Овощи"],
                units["килограмм"],
                PositionType.RAW_MATERIAL,
            ),
            NomenclatureModel(
                "Базилик",
                "Базилик зелёный свежий",
                groups["Овощи"],
                units["грамм"],
                PositionType.RAW_MATERIAL,
            ),
            NomenclatureModel(
                "Тесто для пиццы",
                "Тесто дрожжевое для пиццы",
                groups["Полуфабрикаты"],
                units["килограмм"],
                PositionType.SEMI_FINISHED,
            ),
            NomenclatureModel(
                "Пицца Маргарита",
                "Пицца Маргарита 30 см",
                groups["Блюда"],
                units["штука"],
                PositionType.DISH,
            ),
        ]
        return {position.name: position for position in positions}

    @staticmethod
    def _create_restaurants() -> dict[str, RestaurantModel]:
        """Создаёт рестораны сети."""
        names = ["Ромашка Центральный", "Ромашка Северный"]
        return {name: RestaurantModel(name) for name in names}

    @staticmethod
    def _create_production_shops() -> dict[str, ProductionShopModel]:
        """Создаёт производственный цех."""
        shop = ProductionShopModel("Производственный цех")
        return {shop.name: shop}

    @staticmethod
    def _create_warehouses(
        restaurants: dict[str, RestaurantModel],
        production_shops: dict[str, ProductionShopModel],
    ) -> dict[str, WarehouseModel]:
        """Создаёт центральный склад цеха и склады ресторанов."""
        warehouses = [
            WarehouseModel(
                "Центральный склад цеха",
                PremisesModel(
                    "Холодильный комплекс цеха", "ул. Промышленная, 1", 420.0
                ),
                production_shops["Производственный цех"],
            ),
            WarehouseModel(
                "Склад ресторана Ромашка Центральный",
                PremisesModel(
                    "Складское помещение Центральный", "ул. Ленина, 12", 120.0
                ),
                restaurants["Ромашка Центральный"],
            ),
            WarehouseModel(
                "Склад ресторана Ромашка Северный",
                PremisesModel("Складское помещение Северный", "пр. Мира, 45", 60.5),
                restaurants["Ромашка Северный"],
            ),
        ]
        return {warehouse.name: warehouse for warehouse in warehouses}
