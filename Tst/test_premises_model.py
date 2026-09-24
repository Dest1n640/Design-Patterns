"""Юнит-тесты для Src.models.premises_model.premises_model."""
import pytest

from Src.models.premises_model import premises_model
from Src.Core.exception import validation_exception


def test_ValidPremisesCreated_Constructor_AllFieldsAreSet():
    """Валидное создание помещения сохраняет адрес и площадь."""
    premises = premises_model("Склад №1", "г. Москва, ул. Ленина, 1", 50.0)
    assert premises.name == "Склад №1"
    assert premises.address == "г. Москва, ул. Ленина, 1"
    assert premises.square == 50.0


def test_ValidationException_Constructor_InvalidAddressRaises():
    """Пустой адрес вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        premises_model("Склад №1", "", 50.0)


def test_ValidationException_Constructor_NegativeOrZeroSquareRaises():
    """Неположительная площадь (отрицательная/ноль) вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        premises_model("Склад №1", "г. Москва, ул. Ленина, 1", 0)


def test_ValidationException_Constructor_NonNumericSquareRaises():
    """Нечисловая площадь вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        premises_model("Склад №1", "г. Москва, ул. Ленина, 1", "50")
