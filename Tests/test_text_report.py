"""Юнит-тесты для Src.Logics.Reports.text_report.TextReport."""

import pytest

from Src.Core.exception import ValidationException
from Src.Logics.Reports.text_report import TextReport
from Src.Models.dish_model import DishModel
from Src.Models.nomenclature_model import NomenclatureModel
from Src.Models.technological_map_model import TechnologicalMapModel


def test_text_report__nomenclature__properties_as_columns(groups, units):
    """Номенклатура — одна строка; колонки — её свойства, модели — по имени."""
    flour = NomenclatureModel.create_margherita_nomenclature(groups, units)[0]

    lines = TextReport().build(flour).text.split("\n")

    assert lines == [
        "full_name | group | id | measurement_unit | name | position_type",
        f"Мука пшеничная высшего сорта | Бакалея | {flour.id} | килограмм"
        " | Мука пшеничная | raw_material",
    ]


def test_text_report__measurement_unit__properties_as_columns(units):
    """Единица измерения — одна строка с коэффициентом и базовой единицей."""
    kilogram = units["килограмм"]

    lines = TextReport().build(kilogram).text.split("\n")

    assert lines == [
        "base_coefficient | base_unit | coefficient | id | name",
        f"1000 | грамм | 1000 | {kilogram.id} | килограмм",
    ]


def test_text_report__recipe__row_per_dish(groups, units):
    """Рецепт — строка на каждое блюдо карты; многострочный рецепт в одну строку."""
    recipe = TechnologicalMapModel.create_technological_map(groups, units)
    dough, pizza = recipe.dishes

    report = TextReport().build(recipe)
    lines = report.text.split("\n")

    assert report.name == "Пицца Маргарита"
    assert lines[0] == "id | name | recipe"
    assert len(lines) == 1 + len(recipe.dishes)
    assert lines[1].startswith(f"{dough.id} | Тесто для пиццы | 1. ")
    assert lines[2].startswith(f"{pizza.id} | Пицца Маргарита | 1. ")


def test_text_report__dish__mixed_rows_share_header(groups, units):
    """Ингредиенты и вложенное блюдо в одной таблице: недостающие ячейки пусты."""
    dough, pizza = DishModel.create_margherita_dishes(groups, units)

    lines = TextReport().build(pizza).text.split("\n")

    assert lines[0].split(" | ") == [
        "id",
        "name",
        "recipe",
        "brutto",
        "full_name",
        "group",
        "measurement_unit",
        "netto",
        "position_type",
    ]
    assert len(lines) == 1 + len(pizza.ingredients)
    assert lines[1].endswith(" |  |  |  |  |  | ")


def test_text_report__build__not_a_model_raises():
    """Источник, не являющийся сущностью, вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        TextReport().build("не модель")
