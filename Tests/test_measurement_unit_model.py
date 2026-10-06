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


def test_measurement_unit_model__create_gram__base_unit_without_base():
    """Грамм — корневая единица: без базовой единицы, коэффициент 1."""
    gram = MeasurementUnitModel.create_gram()

    assert (gram.name, gram.coefficient, gram.base_unit) == ("грамм", 1, None)


@pytest.mark.parametrize(
    ("create", "name", "base_name"),
    [
        (MeasurementUnitModel.create_kilogram, "килограмм", "грамм"),
        (MeasurementUnitModel.create_liter, "литр", "миллилитр"),
    ],
)
def test_measurement_unit_model__create_multiple__default_base_unit(
    create, name, base_name
):
    """Кратная единица без переданной базовой создаёт свою, с коэффициентом 1000."""
    unit = create()

    assert (unit.name, unit.base_unit.name) == (name, base_name)
    assert unit.base_coefficient == 1000


def test_measurement_unit_model__create_kilogram__passed_base_unit_is_reused():
    """Переданная базовая единица используется вместо новой."""
    gram = MeasurementUnitModel.create_gram()

    assert MeasurementUnitModel.create_kilogram(gram).base_unit is gram


def test_measurement_unit_model__create_piece__base_unit_without_base():
    """Штука — корневая единица: без базовой единицы, коэффициент 1."""
    piece = MeasurementUnitModel.create_piece()

    assert (piece.name, piece.coefficient, piece.base_unit) == ("штука", 1, None)
