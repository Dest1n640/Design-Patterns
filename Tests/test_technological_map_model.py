"""Юнит-тесты для Src.Models.technological_map_model.TechnologicalMapModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.dish_model import DishModel
from Src.Models.technological_map_model import TechnologicalMapModel


def test_technological_map_model__constructor__without_dishes_is_empty():
    """Карта без переданных блюд создаётся пустой, вес равен нулю."""
    technological_map = TechnologicalMapModel("Карта")

    assert technological_map.dishes == []
    assert technological_map.calculate_netto() == 0
    assert technological_map.calculate_brutto() == 0


def test_technological_map_model__constructor__empty_maps_do_not_share_dishes():
    """Пустые карты не делят один список блюд."""
    first = TechnologicalMapModel("Первая")
    second = TechnologicalMapModel("Вторая")
    first.add_dish(DishModel.create_margherita_dishes()[0])

    assert second.dishes == []


@pytest.mark.parametrize("value", ["блюда", 5, [object()], [None]])
def test_technological_map_model__constructor__invalid_dishes_raises(value):
    """Не список или не блюда вызывают исключение валидации."""
    with pytest.raises(ValidationException):
        TechnologicalMapModel("Карта", value)


def test_technological_map_model__dishes__returns_copy():
    """Изменение полученного списка не меняет блюда карты."""
    technological_map = TechnologicalMapModel.create_technological_map()
    technological_map.dishes.clear()

    assert len(technological_map.dishes) == 2


def test_technological_map_model__add_dish__dish_is_appended():
    """Добавленное блюдо попадает в карту и возвращается в общем списке."""
    technological_map = TechnologicalMapModel("Карта")
    dough = DishModel.create_margherita_dishes()[0]

    result = technological_map.add_dish(dough)

    assert result == [dough]
    assert technological_map.dishes == [dough]


@pytest.mark.parametrize("value", [None, "блюдо", 5])
def test_technological_map_model__add_dish__not_dish_raises(value):
    """Добавление не блюда вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        TechnologicalMapModel("Карта").add_dish(value)


def test_technological_map_model__create_technological_map__margherita_dishes():
    """Фабрика создаёт карту «Пицца Маргарита» из теста и пиццы."""
    technological_map = TechnologicalMapModel.create_technological_map()

    assert technological_map.name == "Пицца Маргарита"
    assert [dish.name for dish in technological_map.dishes] == [
        "Тесто для пиццы",
        "Пицца Маргарита",
    ]


def test_technological_map_model__calculate_netto__sum_of_dishes_netto():
    """Нетто карты — сумма нетто ингредиентов: тесто 160 г + пицца 541 г."""
    technological_map = TechnologicalMapModel.create_technological_map()
    dough, pizza = technological_map.dishes

    assert sum(i.netto for i in dough.ingredients) == 160
    assert sum(i.netto for i in pizza.ingredients) == 541
    assert technological_map.calculate_netto() == 701


def test_technological_map_model__calculate_brutto__sum_of_dishes_brutto():
    """Брутто карты — сумма брутто ингредиентов: тесто 160 г + пицца 541 г."""
    technological_map = TechnologicalMapModel.create_technological_map()
    dough, pizza = technological_map.dishes

    assert sum(i.brutto for i in dough.ingredients) == 160
    assert sum(i.brutto for i in pizza.ingredients) == 541
    assert technological_map.calculate_brutto() == 701


def test_technological_map_model__calculate__netto_and_brutto_differ_when_loss():
    """Нетто и брутто считаются независимо: при потерях они различаются."""
    technological_map = TechnologicalMapModel("Карта")
    dish = DishModel.create_margherita_dishes()[0]
    flour = dish.ingredients[0]
    flour.brutto = 200
    technological_map.add_dish(dish)

    assert technological_map.calculate_brutto() == 210
    assert technological_map.calculate_netto() == 160
