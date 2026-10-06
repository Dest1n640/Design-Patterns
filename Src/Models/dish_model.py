from typing import Self

from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation
from Src.Models.ingredient_model import IngredientModel


class DishModel(NamedModel):
    """Класс блюда — состав из ингредиентов и рецепт приготовления."""

    _INGREDIENTS_ERROR = "Состав блюда указан некорректно"

    def __init__(self, name: str, ingredients: list[IngredientModel], recipe: str):
        """Конструктор блюда."""
        super().__init__(name)
        self.ingredients = ingredients
        self.recipe = recipe

    @property
    def ingredients(self) -> list[IngredientModel]:
        """Возвращает ингредиенты, входящие в состав блюда."""
        return list(self.__ingredients)

    @property
    def recipe(self) -> str:
        """Возвращает рецепт приготовления блюда."""
        return self.__recipe

    @ingredients.setter
    def ingredients(self, new_ingredients: list[IngredientModel]):
        """Устанавливает ингредиенты, входящие в состав блюда."""
        validated = Validation.validate_instance(
            new_ingredients, list, "ingredients", self._INGREDIENTS_ERROR
        )
        if not validated:
            raise ValidationException("ingredients", self._INGREDIENTS_ERROR)
        for ingredient in validated:
            Validation.validate_instance(
                ingredient, IngredientModel, "ingredients", self._INGREDIENTS_ERROR
            )
        self.__ingredients = list(validated)

    @recipe.setter
    def recipe(self, new_recipe: str):
        """Устанавливает рецепт приготовления блюда."""
        self.__recipe = Validation.validate_string(new_recipe, "recipe")

    @classmethod
    def create_margherita_dishes(cls) -> list[Self]:
        """Фабричный метод: создаёт блюда рецепта «Пицца Маргарита».

        Возвращает «Тесто для пиццы» и «Пицца Маргарита» с шагами приготовления
        из _docs/recipes/pizza_margherita.md.
        """
        ingredients = IngredientModel.create_margherita_ingredients()
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
        return [
            cls("Тесто для пиццы", ingredients["Тесто для пиццы"], dough_recipe),
            cls("Пицца Маргарита", ingredients["Пицца Маргарита"], pizza_recipe),
        ]
