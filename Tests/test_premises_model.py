"""Юнит-тесты для Src.Models.premises_model.PremisesModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.premises_model import PremisesModel


def test_premises_model__constructor__all_fields_are_set():
    """Валидное создание помещения сохраняет адрес и площадь."""
    premises = PremisesModel("Склад №1", "г. Москва, ул. Ленина, 1", 50.0)
    assert premises.name == "Склад №1"
    assert premises.address == "г. Москва, ул. Ленина, 1"
    assert premises.square == 50.0


def test_premises_model__constructor__invalid_address_raises():
    """Пустой адрес вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        PremisesModel("Склад №1", "", 50.0)


def test_premises_model__constructor__negative_or_zero_square_raises():
    """Неположительная площадь (отрицательная/ноль) вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        PremisesModel("Склад №1", "г. Москва, ул. Ленина, 1", 0)


def test_premises_model__constructor__non_numeric_square_raises():
    """Нечисловая площадь вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        PremisesModel("Склад №1", "г. Москва, ул. Ленина, 1", "50")
