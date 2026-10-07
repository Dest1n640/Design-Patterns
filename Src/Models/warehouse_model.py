from typing import Self

from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation
from Src.Models.premises_model import PremisesModel
from Src.Models.production_shop_model import ProductionShopModel
from Src.Models.restaurant_model import RestaurantModel


class WarehouseModel(NamedModel):
    """Класс склада — места хранения остатков номенклатуры."""

    def __init__(
        self,
        name: str,
        premises: PremisesModel,
        warehouse_owner: RestaurantModel | ProductionShopModel,
    ):
        """Конструктор склада."""
        super().__init__(name)
        self.premises = premises
        self.warehouse_owner = warehouse_owner

    @property
    def premises(self):
        """Возвращает помещение, в котором расположен склад."""
        return self.__premises

    @property
    def warehouse_owner(self):
        """Возвращает владельца склада."""
        return self.__warehouse_owner

    @premises.setter
    def premises(self, new_premises: PremisesModel):
        """Устанавливает помещение, в котором расположен склад."""
        self.__premises = Validation.validate_instance(
            new_premises, PremisesModel, "premises", "Помещение указано некорректно"
        )

    @warehouse_owner.setter
    def warehouse_owner(
        self, new_warehouse_owner: RestaurantModel | ProductionShopModel
    ):
        """Устанавливает владельца склада: ресторан или производственный цех."""
        self.__warehouse_owner = Validation.validate_instance(
            new_warehouse_owner,
            (RestaurantModel, ProductionShopModel),
            "warehouse_owner",
            "Владелец склада указан некорректно",
        )

    @classmethod
    def create_default_warehouses(
        cls,
        restaurants: dict[str, RestaurantModel],
        production_shops: dict[str, ProductionShopModel],
    ) -> list[Self]:
        """Фабричный метод: создаёт центральный склад цеха и склады ресторанов."""
        return [
            cls(
                "Центральный склад цеха",
                PremisesModel(
                    "Холодильный комплекс цеха", "ул. Промышленная, 1", 420.0
                ),
                production_shops["Производственный цех"],
            ),
            cls(
                "Склад ресторана Ромашка Центральный",
                PremisesModel(
                    "Складское помещение Центральный", "ул. Ленина, 12", 120.0
                ),
                restaurants["Ромашка Центральный"],
            ),
            cls(
                "Склад ресторана Ромашка Северный",
                PremisesModel("Складское помещение Северный", "пр. Мира, 45", 60.5),
                restaurants["Ромашка Северный"],
            ),
        ]
