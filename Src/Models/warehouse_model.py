from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel
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
        self._validate_premises(new_premises)
        self.__premises = new_premises

    @warehouse_owner.setter
    def warehouse_owner(
        self, new_warehouse_owner: RestaurantModel | ProductionShopModel
    ):
        """Устанавливает владельца склада."""
        self._validate_warehouse_owner(new_warehouse_owner)
        self.__warehouse_owner = new_warehouse_owner

    def _validate_premises(self, value: PremisesModel) -> None:
        """Проверка помещения склада: должно быть экземпляром PremisesModel."""
        if not isinstance(value, PremisesModel):
            raise ValidationException("premises", "Помещение указано некорректно")

    def _validate_warehouse_owner(
        self, value: RestaurantModel | ProductionShopModel
    ) -> None:
        """Проверка владельца склада: должен быть рестораном или цехом."""
        if not isinstance(value, (RestaurantModel, ProductionShopModel)):
            raise ValidationException(
                "warehouse_owner", "Владелец склада указан некорректно"
            )
