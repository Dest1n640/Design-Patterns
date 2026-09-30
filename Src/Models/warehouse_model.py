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
