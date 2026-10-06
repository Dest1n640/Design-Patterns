"""Юнит-тесты для Src.Models.ingredient_model.IngredientModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Core.position_type import PositionType
from Src.Models.ingredient_model import IngredientModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel


def _build_ingredient(brutto=120, netto=100):
    """Строит ингредиент с валидными зависимостями и переданными brutto/netto."""
    return IngredientModel(
        "Мука",
        "Мука пшеничная высшего сорта",
        NomenclatureGroupModel("Бакалея"),
        MeasurementUnitModel.create_gram(),
        PositionType.RAW_MATERIAL,
        brutto,
        netto,
    )


def test_ingredient_model__constructor__brutto_and_netto_are_stored():
    """Конструктор сохраняет вес брутто и нетто."""
    ingredient = _build_ingredient(brutto=120.5, netto=100)

    assert ingredient.brutto == 120.5
    assert ingredient.netto == 100


@pytest.mark.parametrize("value", [0, -1, "100", None, True, float("nan")])
def test_ingredient_model__constructor__invalid_brutto_raises(value):
    """Брутто, не являющееся положительным числом, вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _build_ingredient(brutto=value)


@pytest.mark.parametrize("value", [0, -1, "100", None, True, float("inf")])
def test_ingredient_model__constructor__invalid_netto_raises(value):
    """Нетто, не являющееся положительным числом, вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _build_ingredient(netto=value)


def test_ingredient_model__create_margherita__dishes_and_ingredients_count():
    """Фабрика возвращает ингредиенты теста (4) и пиццы (6)."""
    ingredients = IngredientModel.create_margherita_ingredients()

    assert {name: len(items) for name, items in ingredients.items()} == {
        "Тесто для пиццы": 4,
        "Пицца Маргарита": 6,
    }


@pytest.mark.parametrize(
    ("dish", "expected"),
    [
        (
            "Тесто для пиццы",
            {
                "Мука пшеничная": (150, "грамм"),
                "Масло оливковое": (5, "миллилитр"),
                "Соль": (3, "грамм"),
                "Дрожжи сухие": (2, "грамм"),
            },
        ),
        (
            "Пицца Маргарита",
            {
                "Тесто для пиццы": (250, "грамм"),
                "Томаты": (150, "грамм"),
                "Сыр Моцарелла": (125, "грамм"),
                "Масло оливковое": (10, "миллилитр"),
                "Базилик": (5, "грамм"),
                "Соль": (1, "грамм"),
            },
        ),
    ],
)
def test_ingredient_model__create_margherita__quantities_match_recipe(dish, expected):
    """Количества и единицы измерения совпадают с рецептом pizza_margherita.md."""
    ingredients = IngredientModel.create_margherita_ingredients()[dish]

    assert {
        item.name: (item.netto, item.measurement_unit.name) for item in ingredients
    } == expected
    assert all(item.brutto == item.netto for item in ingredients)


def test_ingredient_model__create_margherita__dough_is_semi_finished():
    """Тесто в составе пиццы — полуфабрикат, остальное — сырьё."""
    pizza = IngredientModel.create_margherita_ingredients()["Пицца Маргарита"]

    assert {item.name: item.position_type for item in pizza} == {
        "Тесто для пиццы": PositionType.SEMI_FINISHED,
        "Томаты": PositionType.RAW_MATERIAL,
        "Сыр Моцарелла": PositionType.RAW_MATERIAL,
        "Масло оливковое": PositionType.RAW_MATERIAL,
        "Базилик": PositionType.RAW_MATERIAL,
        "Соль": PositionType.RAW_MATERIAL,
    }
