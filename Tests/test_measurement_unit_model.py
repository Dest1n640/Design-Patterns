"""Юнит-тесты для Src.models.measurement_unit_model.measurement_unit_model."""
import pytest

from Src.models.measurement_unit_model import measurement_unit_model
from Src.Core.exception import validation_exception


def test_base_unit_created_constructor_coefficient_one_and_no_base_unit():
    """Базовая единица измерения: coefficient=1, base_unit=None — создаётся без ошибок."""
    unit = measurement_unit_model("кг", 1)
    assert unit.coefficient == 1
    assert unit.base_unit is None


def test_validation_exception_constructor_no_base_unit_with_coefficient_not_one_raises():
    """base_unit=None при coefficient != 1 — некорректная комбинация, должно быть исключение."""
    with pytest.raises(validation_exception):
        measurement_unit_model("г", 0.001, None)


def test_derived_unit_created_constructor_coefficient_and_base_unit_are_set():
    """Производная единица измерения корректно хранит коэффициент и базовую единицу."""
    kg = measurement_unit_model("кг", 1)
    g = measurement_unit_model("г", 0.001, kg)
    assert g.coefficient == 0.001
    assert g.base_unit is kg


def test_validation_exception_constructor_negative_coefficient_raises():
    """Отрицательный коэффициент вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        measurement_unit_model("г", -1)


def test_validation_exception_constructor_non_numeric_coefficient_raises():
    """Нечисловой коэффициент вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        measurement_unit_model("г", "1")


def test_base_coefficient_computed_base_coefficient_two_level_chain():
    """base_coefficient корректно вычисляется на цепочке из 2 уровней (единица -> базовая)."""
    kg = measurement_unit_model("кг", 1)
    g = measurement_unit_model("г", 0.001, kg)
    assert g.base_coefficient == 0.001


def test_base_coefficient_computed_base_coefficient_three_level_chain():
    """base_coefficient корректно вычисляется на цепочке из 3 уровней (единица -> единица -> базовая)."""
    kg = measurement_unit_model("кг", 1)
    g = measurement_unit_model("г", 0.001, kg)
    mg = measurement_unit_model("мг", 0.001, g)
    assert mg.base_coefficient == 0.001 * 0.001


def test_coefficient_is_updated_coefficient_setter_valid_value_accepted_invalid_raises():
    """Сеттер coefficient принимает валидное значение и бросает исключение на невалидном."""
    unit = measurement_unit_model("кг", 1)
    unit.coefficient = 2
    assert unit.coefficient == 2
    with pytest.raises(validation_exception):
        unit.coefficient = -5
    assert unit.coefficient == 2


def test_base_unit_is_updated_base_unit_setter_valid_value_and_reset_to_none_attempt():
    """Сеттер base_unit принимает валидную единицу и бросает исключение при попытке сброса в None."""
    kg = measurement_unit_model("кг", 1)
    other_kg = measurement_unit_model("кг2", 1)
    g = measurement_unit_model("г", 0.001, kg)
    g.base_unit = other_kg
    assert g.base_unit is other_kg
    with pytest.raises(validation_exception):
        g.base_unit = None
