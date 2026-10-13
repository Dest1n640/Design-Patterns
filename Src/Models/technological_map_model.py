from typing import Self

from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation
from Src.Models.dish_model import DishModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel


class TechnologicalMapModel(NamedModel):
    """Класс технологической карты — набор блюд, приготовляемых по карте."""

    _DISHES_ERROR = "Блюда технологической карты указаны некорректно"

    def __init__(self, name: str, dishes: list[DishModel] | None = None) -> None:
        """Конструктор технологической карты; без блюд карта создаётся пустой."""
        super().__init__(name)
        self.dishes = [] if dishes is None else dishes

    @property
    def dishes(self) -> list[DishModel]:
        """Возвращает блюда технологической карты."""
        return list(self.__dishes)

    @dishes.setter
    def dishes(self, new_dishes: list[DishModel]):
        """Устанавливает блюда технологической карты."""
        validated = Validation.validate_instance(
            new_dishes, list, "dishes", self._DISHES_ERROR
        )
        for dish in validated:
            Validation.validate_instance(dish, DishModel, "dishes", self._DISHES_ERROR)
        self.__dishes = list(validated)

    def add_dish(self, new_dish: DishModel) -> list[DishModel]:
        """Добавляет блюдо в технологическую карту и возвращает все её блюда."""
        validated = Validation.validate_instance(
            new_dish, DishModel, "dishes", self._DISHES_ERROR
        )
        self.__dishes.append(validated)
        return self.dishes

    @classmethod
    def create_technological_map(
        cls,
        groups: dict[str, NomenclatureGroupModel],
        units: dict[str, MeasurementUnitModel],
    ) -> Self:
        """Фабричный метод: создаёт составную карту «Пицца Маргарита»."""
        return cls("Пицца Маргарита", DishModel.create_margherita_dishes(groups, units))
