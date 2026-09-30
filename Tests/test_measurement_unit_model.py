"""Юнит-тесты для Src.Models.measurement_unit_model.MeasurementUnitModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.measurement_unit_model import MeasurementUnitModel


def test_measurement_unit_model__base_coefficient__no_base_unit_equals_coefficient():
    """У базовой единицы итоговый коэффициент равен её собственному."""
    kg = MeasurementUnitModel("кг", 1)
    assert kg.base_coefficient == 1


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


def test_measurement_unit_model__constructor__coefficient_not_1_no_base_unit_raises():
    """base_unit=None при coefficient != 1 — некорректная комбинация, ошибка."""
    with pytest.raises(ValidationException):
        MeasurementUnitModel("г", 0.001, None)


def test_measurement_unit_model__constructor__non_unit_base_unit_raises():
    """Базовая единица, не являющаяся MeasurementUnitModel, вызывает исключение."""
    with pytest.raises(ValidationException):
        MeasurementUnitModel("г", 0.001, "кг")


def test_measurement_unit_model__base_unit_setter__reset_to_none_raises():
    """Сброс base_unit в None при coefficient != 1 бросает и не меняет значение."""
    kg = MeasurementUnitModel("кг", 1)
    g = MeasurementUnitModel("г", 0.001, kg)
    with pytest.raises(ValidationException):
        g.base_unit = None
    assert g.base_unit is kg
