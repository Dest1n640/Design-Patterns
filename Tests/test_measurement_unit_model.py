"""Юнит-тесты для Src.Models.measurement_unit_model.MeasurementUnitModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.measurement_unit_model import MeasurementUnitModel


def test_measurement_unit_model__base_coefficient__no_base_unit_equals_coefficient():
    """У базовой единицы итоговый коэффициент равен её собственному."""
    # Подготовка
    kg = MeasurementUnitModel("кг", 1)

    # Действия
    coefficient = kg.base_coefficient

    # Проверки
    assert coefficient == 1


def test_measurement_unit_model__base_coefficient__two_level_chain_is_computed():
    """Итоговый коэффициент корректно вычисляется на цепочке из 2 уровней."""
    # Подготовка
    kg = MeasurementUnitModel("кг", 1)
    g = MeasurementUnitModel("г", 0.001, kg)

    # Действия
    coefficient = g.base_coefficient

    # Проверки
    assert coefficient == 0.001


def test_measurement_unit_model__base_coefficient__three_level_chain_is_computed():
    """Итоговый коэффициент корректно вычисляется на цепочке из 3 уровней."""
    # Подготовка
    kg = MeasurementUnitModel("кг", 1)
    g = MeasurementUnitModel("г", 0.001, kg)
    mg = MeasurementUnitModel("мг", 0.001, g)

    # Действия
    coefficient = mg.base_coefficient

    # Проверки
    assert coefficient == 0.001 * 0.001


def test_measurement_unit_model__constructor__coefficient_not_1_no_base_unit_raises():
    """Коэффициент, отличный от 1, без базовой единицы вызывает исключение."""
    # Подготовка
    coefficient = 0.001

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        MeasurementUnitModel("г", coefficient, None)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_measurement_unit_model__constructor__non_unit_base_unit_raises():
    """Базовая единица, не являющаяся MeasurementUnitModel, вызывает исключение."""
    # Подготовка
    base_unit = "кг"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        MeasurementUnitModel("г", 0.001, base_unit)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_measurement_unit_model__base_unit_setter__reset_to_none_raises():
    """Сброс base_unit в None при coefficient != 1 бросает и не меняет значение."""
    # Подготовка
    kg = MeasurementUnitModel("кг", 1)
    g = MeasurementUnitModel("г", 0.001, kg)

    # Действия
    with pytest.raises(ValidationException):
        g.base_unit = None

    # Проверки
    assert g.base_unit is kg


def test_measurement_unit_model__create_gram__base_unit_without_base():
    """Грамм — корневая единица: без базовой единицы, коэффициент 1."""
    # Подготовка
    # Дополнительная подготовка не требуется.

    # Действия
    gram = MeasurementUnitModel.create_gram()

    # Проверки
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
    # Подготовка
    # Фабрика и ожидаемые имена заданы параметризацией.

    # Действия
    unit = create()

    # Проверки
    assert (unit.name, unit.base_unit.name) == (name, base_name)
    assert unit.base_coefficient == 1000


def test_measurement_unit_model__create_kilogram__passed_base_unit_is_reused():
    """Переданная базовая единица используется вместо новой."""
    # Подготовка
    gram = MeasurementUnitModel.create_gram()

    # Действия
    kilogram = MeasurementUnitModel.create_kilogram(gram)

    # Проверки
    assert kilogram.base_unit is gram


def test_measurement_unit_model__create_piece__base_unit_without_base():
    """Штука — корневая единица: без базовой единицы, коэффициент 1."""
    # Подготовка
    # Дополнительная подготовка не требуется.

    # Действия
    piece = MeasurementUnitModel.create_piece()

    # Проверки
    assert (piece.name, piece.coefficient, piece.base_unit) == ("штука", 1, None)
