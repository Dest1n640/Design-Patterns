"""Юнит-тесты для Src.Models.dish_model.DishModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.dish_model import DishModel
from Src.Models.ingredient_model import IngredientModel


def _build_ingredients(groups, units):
    """Возвращает валидный состав блюда из рецепта теста."""
    return IngredientModel.create_margherita_ingredients(groups, units)[
        "Тесто для пиццы"
    ]


def test_dish_model__constructor__fields_are_stored(groups, units):
    """Конструктор сохраняет имя, состав и рецепт блюда."""
    ingredients = _build_ingredients(groups, units)
    dish = DishModel("Тесто", ingredients, "Замесить.")

    assert (dish.name, dish.ingredients, dish.recipe) == (
        "Тесто",
        ingredients,
        "Замесить.",
    )


def test_dish_model__ingredients__returns_copy(groups, units):
    """Изменение полученного списка не меняет состав блюда."""
    dish = DishModel("Тесто", _build_ingredients(groups, units), "Замесить.")
    dish.ingredients.clear()

    assert len(dish.ingredients) == 4


def test_dish_model__ingredients__source_list_change_does_not_affect_dish(
    groups, units
):
    """Изменение исходного списка после создания блюда не меняет состав блюда."""
    ingredients = _build_ingredients(groups, units)
    dish = DishModel("Тесто", ingredients, "Замесить.")
    ingredients.clear()

    assert len(dish.ingredients) == 4


@pytest.mark.parametrize("value", [[], "состав", None, [object()], [None]])
def test_dish_model__constructor__invalid_ingredients_raises(value):
    """Пустой состав, не список или не ингредиенты вызывают исключение валидации."""
    with pytest.raises(ValidationException):
        DishModel("Тесто", value, "Замесить.")


@pytest.mark.parametrize("value", ["", "   ", None, 5])
def test_dish_model__constructor__invalid_recipe_raises(value, groups, units):
    """Пустой рецепт или не строка вызывают исключение валидации."""
    with pytest.raises(ValidationException):
        DishModel("Тесто", _build_ingredients(groups, units), value)


def test_dish_model__create_margherita__dishes_with_recipe_steps(groups, units):
    """Фабрика возвращает тесто (4 шага) и пиццу (7 шагов) с рецептами."""
    dough, pizza = DishModel.create_margherita_dishes(groups, units)

    assert (dough.name, len(dough.recipe.splitlines())) == ("Тесто для пиццы", 4)
    assert (pizza.name, len(pizza.recipe.splitlines())) == ("Пицца Маргарита", 7)


def test_dish_model__create_margherita__ingredients_count(groups, units):
    """У теста 4 ингредиента, у пиццы — 6 (включая тесто)."""
    dough, pizza = DishModel.create_margherita_dishes(groups, units)

    assert (len(dough.ingredients), len(pizza.ingredients)) == (4, 6)


def test_dish_model__create_margherita__pizza_contains_dough_dish(groups, units):
    """Полуфабрикат «Тесто для пиццы» входит в пиццу тем же объектом блюда."""
    dough, pizza = DishModel.create_margherita_dishes(groups, units)

    assert pizza.ingredients[0] is dough


def test_dish_model__calculate_netto__nested_dish_is_counted_recursively(groups, units):
    """Нетто пиццы включает нетто теста: тесто 160 г, пицца 160 + 291 = 451 г."""
    dough, pizza = DishModel.create_margherita_dishes(groups, units)

    assert (dough.calculate_netto(), pizza.calculate_netto()) == (160, 451)


def test_dish_model__calculate_brutto__nested_dish_is_counted_recursively(
    groups, units
):
    """Брутто пиццы включает брутто теста: тесто 160 г, пицца 160 + 291 = 451 г."""
    dough, pizza = DishModel.create_margherita_dishes(groups, units)

    assert (dough.calculate_brutto(), pizza.calculate_brutto()) == (160, 451)


def test_dish_model__calculate__nested_dish_change_changes_weight(groups, units):
    """Изменение ингредиента теста (мука: брутто 200) меняет вес пиццы."""
    dough, pizza = DishModel.create_margherita_dishes(groups, units)
    dough.ingredients[0].brutto = 200

    assert (pizza.calculate_brutto(), pizza.calculate_netto()) == (501, 451)


def test_dish_model__calculate__netto_and_brutto_differ_when_loss(groups, units):
    """Нетто и брутто считаются независимо: при потерях они различаются."""
    dough = DishModel.create_margherita_dishes(groups, units)[0]
    dough.ingredients[0].brutto = 200

    assert (dough.calculate_brutto(), dough.calculate_netto()) == (210, 160)


def test_dish_model__calculate__add_ingredient_increases_weight(groups, units):
    """Добавление ингредиента (томаты: брутто 180, нетто 150) увеличивает вес."""
    dough, pizza = DishModel.create_margherita_dishes(groups, units)
    tomatoes = pizza.ingredients[1]
    tomatoes.brutto = 180

    dough.ingredients = [*dough.ingredients, tomatoes]

    assert (dough.calculate_brutto(), dough.calculate_netto()) == (340, 310)


def test_dish_model__calculate__remove_ingredient_decreases_weight(groups, units):
    """Исключение муки (150 г) уменьшает вес теста со 160 до 10 г."""
    dough = DishModel.create_margherita_dishes(groups, units)[0]

    dough.ingredients = dough.ingredients[1:]

    assert (dough.calculate_brutto(), dough.calculate_netto()) == (10, 10)
