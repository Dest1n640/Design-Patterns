"""Юнит-тесты для Src.Models.nomenclature_model.NomenclatureModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Core.position_type import PositionType
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.nomenclature_model import NomenclatureModel


def _build_nomenclature(name="Мука", full_name="Мука пшеничная высший сорт"):
    """Строит номенклатуру с валидными зависимостями и переданными name/full_name."""
    group = NomenclatureGroupModel("Бакалея")
    unit = MeasurementUnitModel("кг", 1)
    return NomenclatureModel(name, full_name, group, unit, PositionType.RAW_MATERIAL)


def test_nomenclature_model__constructor__all_fields_are_set():
    """Валидное создание номенклатуры сохраняет все переданные поля."""
    nomenclature = _build_nomenclature()
    assert nomenclature.name == "Мука"
    assert nomenclature.full_name == "Мука пшеничная высший сорт"
    assert nomenclature.position_type == PositionType.RAW_MATERIAL


def test_nomenclature_model__constructor__name_longer_than_50_raises():
    """Имя длиннее 50 символов вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _build_nomenclature(name="Н" * 51)


def test_nomenclature_model__constructor__empty_name_raises():
    """Пустое имя вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _build_nomenclature(name="")


def test_nomenclature_model__constructor__full_name_longer_than_255_raises():
    """Полное наименование длиннее 255 символов вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _build_nomenclature(full_name="Н" * 256)


def test_nomenclature_model__constructor__empty_full_name_raises():
    """Пустое полное наименование вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _build_nomenclature(full_name="")


def test_nomenclature_model__full_name_setter__valid_value_accepted():
    """Сеттер full_name принимает значение длиннее 50 символов."""
    nomenclature = _build_nomenclature()
    long_value = "Мука пшеничная высшего сорта особого урожая, произведённая по ГОСТ"
    nomenclature.full_name = long_value
    assert nomenclature.full_name == long_value


def test_nomenclature_model__full_name_setter__invalid_value_raises():
    """Сеттер full_name бросает исключение валидации на невалидном значении."""
    nomenclature = _build_nomenclature()
    with pytest.raises(ValidationException):
        nomenclature.full_name = ""
