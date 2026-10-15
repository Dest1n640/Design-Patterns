"""Юнит-тесты для Src.Logics.Reports.text_report.TextReport."""

import pytest

from Src.Core.exception import ValidationException
from Src.Logics.Reports.text_report import TextReport
from Src.Models.dish_model import DishModel

HEADER = "Код | Наименование | Брутто | Нетто"


def test_text_report__build__row_per_ingredient(groups, units):
    """Отчёт: заголовок и по строке на каждый ингредиент; имя отчёта — имя блюда."""
    dough, _ = DishModel.create_margherita_dishes(groups, units)
    flour = dough.ingredients[0]

    report = TextReport().build(dough)
    lines = report.text.split("\n")

    assert report.name == dough.name
    assert lines[0] == HEADER
    assert len(lines) == 1 + len(dough.ingredients)
    assert lines[1] == f"{flour.id} | Мука пшеничная | 150 | 150"


def test_text_report__build__nested_dish_weight_is_summed(groups, units):
    """Вложенное блюдо (тесто) выводится одной строкой с суммарным весом."""
    dough, pizza = DishModel.create_margherita_dishes(groups, units)

    lines = TextReport().build(pizza).text.split("\n")

    assert lines[1] == f"{dough.id} | Тесто для пиццы | 160 | 160"


def test_text_report__build__not_a_dish_raises():
    """Источник, не являющийся блюдом, вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        TextReport().build("не блюдо")
