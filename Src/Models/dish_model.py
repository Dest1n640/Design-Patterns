from typing import Self

from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation
from Src.Models.ingredient_model import IngredientModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel


class DishModel(NamedModel):
    """Класс блюда — состав из ингредиентов и вложенных блюд, рецепт приготовления."""

    _INGREDIENTS_ERROR = "Состав блюда указан некорректно"

    def __init__(
        self, name: str, ingredients: list[IngredientModel | Self], recipe: str
    ):
        """Конструктор блюда."""
        super().__init__(name)
        self.ingredients = ingredients
        self.recipe = recipe

    @property
    def ingredients(self) -> list[IngredientModel | Self]:
        """Возвращает состав блюда: ингредиенты и вложенные блюда-полуфабрикаты."""
        return list(self.__ingredients)

    @property
    def recipe(self) -> str:
        """Возвращает рецепт приготовления блюда."""
        return self.__recipe

    @ingredients.setter
    def ingredients(self, new_ingredients: list[IngredientModel | Self]):
        """Устанавливает состав блюда: ингредиенты и вложенные блюда-полуфабрикаты."""
        validated = Validation.validate_instance(
            new_ingredients, list, "ingredients", self._INGREDIENTS_ERROR
        )
        if not validated:
            raise ValidationException("ingredients", self._INGREDIENTS_ERROR)
        for ingredient in validated:
            Validation.validate_instance(
                ingredient,
                (IngredientModel, DishModel),
                "ingredients",
                self._INGREDIENTS_ERROR,
            )
        self.__ingredients = list(validated)

    @recipe.setter
    def recipe(self, new_recipe: str):
        """Устанавливает рецепт приготовления блюда."""
        self.__recipe = Validation.validate_string(new_recipe, "recipe")

    def calculate_netto(self) -> int | float:
        """Возвращает вес нетто блюда; вложенные блюда считаются рекурсивно."""
        return sum(
            item.calculate_netto() if isinstance(item, DishModel) else item.netto
            for item in self.ingredients
        )

    def calculate_brutto(self) -> int | float:
        """Возвращает вес брутто блюда; вложенные блюда считаются рекурсивно."""
        return sum(
            item.calculate_brutto() if isinstance(item, DishModel) else item.brutto
            for item in self.ingredients
        )

    @classmethod
    def create_margherita_dishes(
        cls,
        groups: dict[str, NomenclatureGroupModel],
        units: dict[str, MeasurementUnitModel],
    ) -> list[Self]:
        """Фабричный метод: создаёт тесто и пиццу, в которую тесто входит блюдом."""
        ingredients = IngredientModel.create_margherita_ingredients(groups, units)
        dough_recipe = "\n".join(
            [
                "1. Растворить дрожжи в тёплой воде (35–38 °C) и оставить "
                "на 10 минут до появления пены.",
                "2. Смешать муку с солью, влить воду с дрожжами и оливковое масло.",
                "3. Вымешивать 8–10 минут до гладкого эластичного теста, "
                "которое не липнет к рукам.",
                "4. Скатать в шар, накрыть и оставить в тёплом месте на "
                "1–1,5 часа, пока тесто не увеличится в объёме вдвое.",
            ]
        )
        pizza_recipe = "\n".join(
            [
                "1. Разогреть духовку до 250–280 °C вместе с камнем для пиццы "
                "или перевёрнутым противнем.",
                "2. Надрезать томаты крестом, опустить в кипяток на 30 секунд, "
                "снять кожицу и измельчить в соус с солью.",
                "3. Растянуть тесто руками в круг диаметром 30 см, "
                "оставив бортик 1–1,5 см.",
                "4. Распределить томатный соус по тесту, не заходя на бортик.",
                "5. Выложить моцареллу небольшими кусочками и сбрызнуть "
                "оливковым маслом.",
                "6. Выпекать 7–10 минут, пока бортик не станет золотистым, "
                "а сыр не расплавится.",
                "7. Сразу после выпечки выложить листья базилика.",
            ]
        )
        dough = cls("Тесто для пиццы", ingredients["Тесто для пиццы"], dough_recipe)
        pizza = cls(
            "Пицца Маргарита",
            [dough, *ingredients["Пицца Маргарита"]],
            pizza_recipe,
        )
        return [dough, pizza]
