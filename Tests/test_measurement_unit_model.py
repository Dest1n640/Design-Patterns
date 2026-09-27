"""Юнит-тесты для Src.Models.measurement_unit_model.MeasurementUnitModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.measurement_unit_model import MeasurementUnitModel


def test_measurement_unit_model__constructor__base_unit_with_coefficient_one():
    """Базовая единица: coefficient=1, base_unit=None — создаётся без ошибок."""
    unit = MeasurementUnitModel("кг", 1)
    assert unit.coefficient == 1
    assert unit.base_unit is None


def test_measurement_unit_model__constructor__coefficient_not_1_no_base_unit_raises():
    """base_unit=None при coefficient != 1 — некорректная комбинация, ошибка."""
    with pytest.raises(ValidationException):
        MeasurementUnitModel("г", 0.001, None)


def test_measurement_unit_model__constructor__derived_unit_fields_are_set():
    """Производная единица измерения корректно хранит коэффициент и базовую единицу."""
    kg = MeasurementUnitModel("кг", 1)
    g = MeasurementUnitModel("г", 0.001, kg)
    assert g.coefficient == 0.001
    assert g.base_unit is kg


def test_measurement_unit_model__constructor__negative_coefficient_raises():
    """Отрицательный коэффициент вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        MeasurementUnitModel("г", -1)


def test_measurement_unit_model__constructor__non_numeric_coefficient_raises():
    """Нечисловой коэффициент вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        MeasurementUnitModel("г", "1")


def test_measurement_unit_model__base_coefficient__two_level_chain_is_computed():
    """base_coefficient корректно вычисляется на цепочке из 2 уровней."""
    kg = MeasurementUnitModel("кг", 1)
    g = MeasurementUnitModel("г", 0.001, kg)
    assert g.base_coefficient == 0.001


def test_measurement_unit_model__base_coefficient__three_level_chain_is_computed():
    """base_coefficient корректно вычисляется на цепочке из 3 уровней."""
    kg = MeasurementUnitModel("кг", 1)
    g = MeasurementUnitModel("г", 0.001, kg)
    mg = MeasurementUnitModel("мг", 0.001, g)
    assert mg.base_coefficient == 0.001 * 0.001


def test_measurement_unit_model__coefficient_setter__valid_accepted_invalid_raises():
    """Сеттер coefficient принимает валидное значение и бросает на невалидном."""
    unit = MeasurementUnitModel("кг", 1)
    unit.coefficient = 2
    assert unit.coefficient == 2
    with pytest.raises(ValidationException):
        unit.coefficient = -5
    assert unit.coefficient == 2


def test_measurement_unit_model__base_unit_setter__reset_to_none_raises():
    """Сеттер base_unit принимает валидную единицу и бросает при сбросе в None."""
    kg = MeasurementUnitModel("кг", 1)
    other_kg = MeasurementUnitModel("кг2", 1)
    g = MeasurementUnitModel("г", 0.001, kg)
    g.base_unit = other_kg
    assert g.base_unit is other_kg
    with pytest.raises(ValidationException):
        g.base_unit = None
