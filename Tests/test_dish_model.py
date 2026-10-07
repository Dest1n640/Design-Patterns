"""Юнит-тесты для Src.Models.dish_model.DishModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.dish_model import DishModel
from Src.Models.ingredient_model import IngredientModel


def _build_ingredients():
    """Возвращает валидный состав блюда из рецепта теста."""
    return IngredientModel.create_margherita_ingredients()["Тесто для пиццы"]


def test_dish_model__constructor__fields_are_stored():
    """Конструктор сохраняет имя, состав и рецепт блюда."""
    ingredients = _build_ingredients()
    dish = DishModel("Тесто", ingredients, "Замесить.")

    assert (dish.name, dish.ingredients, dish.recipe) == (
        "Тесто",
        ingredients,
        "Замесить.",
    )


def test_dish_model__ingredients__returns_copy():
    """Изменение полученного списка не меняет состав блюда."""
    dish = DishModel("Тесто", _build_ingredients(), "Замесить.")
    dish.ingredients.clear()

    assert len(dish.ingredients) == 4


def test_dish_model__ingredients__source_list_change_does_not_affect_dish():
    """Изменение исходного списка после создания блюда не меняет состав блюда."""
    ingredients = _build_ingredients()
    dish = DishModel("Тесто", ingredients, "Замесить.")
    ingredients.clear()

    assert len(dish.ingredients) == 4


@pytest.mark.parametrize("value", [[], "состав", None, [object()], [None]])
def test_dish_model__constructor__invalid_ingredients_raises(value):
    """Пустой состав, не список или не ингредиенты вызывают исключение валидации."""
    with pytest.raises(ValidationException):
        DishModel("Тесто", value, "Замесить.")


@pytest.mark.parametrize("value", ["", "   ", None, 5])
def test_dish_model__constructor__invalid_recipe_raises(value):
    """Пустой рецепт или не строка вызывают исключение валидации."""
    with pytest.raises(ValidationException):
        DishModel("Тесто", _build_ingredients(), value)


def test_dish_model__create_margherita__dishes_with_recipe_steps():
    """Фабрика возвращает тесто (4 шага) и пиццу (7 шагов) с рецептами."""
    dough, pizza = DishModel.create_margherita_dishes()

    assert (dough.name, len(dough.recipe.splitlines())) == ("Тесто для пиццы", 4)
    assert (pizza.name, len(pizza.recipe.splitlines())) == ("Пицца Маргарита", 7)


def test_dish_model__create_margherita__ingredients_count():
    """У теста 4 ингредиента, у пиццы — 6."""
    dough, pizza = DishModel.create_margherita_dishes()

    assert (len(dough.ingredients), len(pizza.ingredients)) == (4, 6)


def test_dish_model__calculate_netto__sum_of_ingredients_netto():
    """Нетто блюда — сумма нетто ингредиентов: тесто 160 г, пицца 541 г."""
    dough, pizza = DishModel.create_margherita_dishes()

    assert (dough.calculate_netto(), pizza.calculate_netto()) == (160, 541)


def test_dish_model__calculate_brutto__sum_of_ingredients_brutto():
    """Брутто блюда — сумма брутто ингредиентов: тесто 160 г, пицца 541 г."""
    dough, pizza = DishModel.create_margherita_dishes()

    assert (dough.calculate_brutto(), pizza.calculate_brutto()) == (160, 541)


def test_dish_model__calculate__netto_and_brutto_differ_when_loss():
    """Нетто и брутто считаются независимо: при потерях они различаются."""
    dough = DishModel.create_margherita_dishes()[0]
    dough.ingredients[0].brutto = 200

    assert (dough.calculate_brutto(), dough.calculate_netto()) == (210, 160)
