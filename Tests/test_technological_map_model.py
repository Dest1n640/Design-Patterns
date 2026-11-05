"""Юнит-тесты для Src.Models.technological_map_model.TechnologicalMapModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.dish_model import DishModel
from Src.Models.technological_map_model import TechnologicalMapModel


def test_technological_map_model__constructor__without_dishes_is_empty():
    """Карта без переданных блюд создаётся пустой, вес равен нулю."""
    # Подготовка
    name = "Карта"

    # Действия
    technological_map = TechnologicalMapModel(name)

    # Проверки
    assert technological_map.dishes == []


def test_technological_map_model__constructor__empty_maps_do_not_share_dishes(
    groups, units
):
    """Пустые карты не делят один список блюд."""
    # Подготовка
    first = TechnologicalMapModel("Первая")
    second = TechnologicalMapModel("Вторая")
    dough = DishModel.create_margherita_dishes(groups, units)[0]

    # Действия
    first.add_dish(dough)

    # Проверки
    assert second.dishes == []


@pytest.mark.parametrize("value", ["блюда", 5, [object()], [None]])
def test_technological_map_model__constructor__invalid_dishes_raises(value):
    """Не список или не блюда вызывают исключение валидации."""
    # Подготовка
    name = "Карта"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        TechnologicalMapModel(name, value)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_technological_map_model__dishes__returns_copy(groups, units):
    """Изменение полученного списка не меняет блюда карты."""
    # Подготовка
    technological_map = TechnologicalMapModel.create_technological_map(groups, units)

    # Действия
    technological_map.dishes.clear()

    # Проверки
    assert len(technological_map.dishes) == 2


def test_technological_map_model__add_dish__dish_is_appended(groups, units):
    """Добавленное блюдо попадает в карту и возвращается в общем списке."""
    # Подготовка
    technological_map = TechnologicalMapModel("Карта")
    dough = DishModel.create_margherita_dishes(groups, units)[0]

    # Действия
    result = technological_map.add_dish(dough)

    # Проверки
    assert result == [dough]
    assert technological_map.dishes == [dough]


@pytest.mark.parametrize("value", [None, "блюдо", 5])
def test_technological_map_model__add_dish__not_dish_raises(value):
    """Добавление не блюда вызывает исключение валидации."""
    # Подготовка
    technological_map = TechnologicalMapModel("Карта")

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        technological_map.add_dish(value)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_technological_map_model__create_technological_map__margherita_dishes(
    groups, units
):
    """Фабрика создаёт карту «Пицца Маргарита» из теста и пиццы."""
    # Подготовка
    # Справочники подготовлены фикстурами groups и units.

    # Действия
    technological_map = TechnologicalMapModel.create_technological_map(groups, units)

    # Проверки
    assert technological_map.name == "Пицца Маргарита"
    assert [dish.name for dish in technological_map.dishes] == [
        "Тесто для пиццы",
        "Пицца Маргарита",
    ]
