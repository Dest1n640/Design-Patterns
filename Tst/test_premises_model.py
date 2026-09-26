"""Юнит-тесты для Src.models.premises_model.premises_model."""
import pytest

from Src.models.premises_model import premises_model
from Src.Core.exception import validation_exception


def test_valid_premises_created_constructor_all_fields_are_set():
    """Валидное создание помещения сохраняет адрес и площадь."""
    premises = premises_model("Склад №1", "г. Москва, ул. Ленина, 1", 50.0)
    assert premises.name == "Склад №1"
    assert premises.address == "г. Москва, ул. Ленина, 1"
    assert premises.square == 50.0


def test_validation_exception_constructor_invalid_address_raises():
    """Пустой адрес вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        premises_model("Склад №1", "", 50.0)


def test_validation_exception_constructor_negative_or_zero_square_raises():
    """Неположительная площадь (отрицательная/ноль) вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        premises_model("Склад №1", "г. Москва, ул. Ленина, 1", 0)


def test_validation_exception_constructor_non_numeric_square_raises():
    """Нечисловая площадь вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        premises_model("Склад №1", "г. Москва, ул. Ленина, 1", "50")
