from Src.Core.named_entity import named_entity
from Src.Core.exception import validation_exception
from Src.models.premises_model import premises_model
from Src.models.restaurant_model import restaurant_model
from Src.models.production_shop_model import production_shop_model

class warehouse_model(named_entity):
    """Класс склада — места хранения остатков номенклатуры"""

    def __init__(self, name: str, premises: premises_model, warehouse_owner: restaurant_model | production_shop_model):
        """
        Конструктор склада

        :premises: помещение, в котором расположен склад
        :warehouse_owner: владелец склада — ресторан или производственный цех
        """
        super().__init__(name)
        self.premises = premises
        self.warehouse_owner = warehouse_owner

    @property
    def premises(self):
        """Возвращает помещение, в котором расположен склад"""
        return self.__premises

    @property
    def warehouse_owner(self):
        """Возвращает владельца склада"""
        return self.__warehouse_owner

    @premises.setter
    def premises(self, new_premises: premises_model):
        """
        Устанавливает помещение, в котором расположен склад

        :new_premises: новое помещение
        """
        self._validate_premises(new_premises)
        self.__premises = new_premises

    @warehouse_owner.setter
    def warehouse_owner(self, new_warehouse_owner: restaurant_model | production_shop_model):
        """
        Устанавливает владельца склада

        :new_warehouse_owner: новый владелец склада
        """
        self._validate_warehouse_owner(new_warehouse_owner)
        self.__warehouse_owner = new_warehouse_owner

    def _validate_premises(self, value: premises_model) -> None:
        """
        Проверка помещения склада: должно быть экземпляром premises_model

        :value: проверяемое помещение
        """
        if not isinstance(value, premises_model):
            raise validation_exception("premises", "Помещение указано некорректно")

    def _validate_warehouse_owner(self, value: restaurant_model | production_shop_model) -> None:
        """
        Проверка владельца склада: должен быть рестораном или производственным цехом

        :value: проверяемый владелец склада
        """
        if not isinstance(value, (restaurant_model, production_shop_model)):
            raise validation_exception("warehouse_owner", "Владелец склада указан некорректно")
