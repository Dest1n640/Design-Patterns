"""Юнит-тесты для Src.models.measurement_unit_model.measurement_unit_model."""
import pytest

from Src.models.measurement_unit_model import measurement_unit_model
from Src.Core.exception import validation_exception


def test_BaseUnitCreated_Constructor_CoefficientOneAndNoBaseUnit():
    """Базовая единица измерения: coefficient=1, base_unit=None — создаётся без ошибок."""
    unit = measurement_unit_model("кг", 1)
    assert unit.coefficient == 1
    assert unit.base_unit is None


def test_ValidationException_Constructor_NoBaseUnitWithCoefficientNotOneRaises():
    """base_unit=None при coefficient != 1 — некорректная комбинация, должно быть исключение."""
    with pytest.raises(validation_exception):
        measurement_unit_model("г", 0.001, None)


def test_DerivedUnitCreated_Constructor_CoefficientAndBaseUnitAreSet():
    """Производная единица измерения корректно хранит коэффициент и базовую единицу."""
    kg = measurement_unit_model("кг", 1)
    g = measurement_unit_model("г", 0.001, kg)
    assert g.coefficient == 0.001
    assert g.base_unit is kg


def test_ValidationException_Constructor_NegativeCoefficientRaises():
    """Отрицательный коэффициент вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        measurement_unit_model("г", -1)


def test_ValidationException_Constructor_NonNumericCoefficientRaises():
    """Нечисловой коэффициент вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        measurement_unit_model("г", "1")


def test_BaseCoefficientComputed_BaseCoefficient_TwoLevelChain():
    """base_coefficient корректно вычисляется на цепочке из 2 уровней (единица -> базовая)."""
    kg = measurement_unit_model("кг", 1)
    g = measurement_unit_model("г", 0.001, kg)
    assert g.base_coefficient == 0.001


def test_BaseCoefficientComputed_BaseCoefficient_ThreeLevelChain():
    """base_coefficient корректно вычисляется на цепочке из 3 уровней (единица -> единица -> базовая)."""
    kg = measurement_unit_model("кг", 1)
    g = measurement_unit_model("г", 0.001, kg)
    mg = measurement_unit_model("мг", 0.001, g)
    assert mg.base_coefficient == 0.001 * 0.001


def test_CoefficientIsUpdated_CoefficientSetter_ValidValueAcceptedInvalidRaises():
    """Сеттер coefficient принимает валидное значение и бросает исключение на невалидном."""
    unit = measurement_unit_model("кг", 1)
    unit.coefficient = 2
    assert unit.coefficient == 2
    with pytest.raises(validation_exception):
        unit.coefficient = -5
    assert unit.coefficient == 2


def test_BaseUnitIsUpdated_BaseUnitSetter_ValidValueAndResetToNoneAttempt():
    """Сеттер base_unit принимает валидную единицу и бросает исключение при попытке сброса в None."""
    kg = measurement_unit_model("кг", 1)
    other_kg = measurement_unit_model("кг2", 1)
    g = measurement_unit_model("г", 0.001, kg)
    g.base_unit = other_kg
    assert g.base_unit is other_kg
    with pytest.raises(validation_exception):
        g.base_unit = None
