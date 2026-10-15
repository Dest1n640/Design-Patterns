"""Юнит-тесты для Src.Logics.Reports.binary_report.BinaryReport."""

import pickle

import pytest

from Src.Core.exception import ValidationException
from Src.Logics.Reports.binary_report import BinaryReport
from Src.Models.dish_model import DishModel


def test_binary_report__build__bytes_restore_same_dish(groups, units):
    """Байты отчёта восстанавливаются в то же блюдо; текст отчёта пуст."""
    _, pizza = DishModel.create_margherita_dishes(groups, units)

    report = BinaryReport().build(pizza)
    restored = pickle.loads(report.binary)

    assert report.name == pizza.name
    assert report.text == ""
    assert restored.id == pizza.id
    assert len(restored.ingredients) == len(pizza.ingredients)


def test_binary_report__build__not_a_dish_raises():
    """Источник, не являющийся блюдом, вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        BinaryReport().build("не блюдо")
