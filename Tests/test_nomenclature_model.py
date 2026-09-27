"""Юнит-тесты для Src.models.nomenclature_model.nomenclature_model."""
import pytest

from Src.models.nomenclature_model import nomenclature_model
from Src.models.nomenclature_group_model import nomenclature_group_model
from Src.models.measurement_unit_model import measurement_unit_model
from Src.Core.position_type import position_type
from Src.Core.exception import validation_exception


def _build_nomenclature(name="Мука", full_name="Мука пшеничная высший сорт"):
    """Строит номенклатуру с валидными зависимостями и переданными name/full_name."""
    group = nomenclature_group_model("Бакалея")
    unit = measurement_unit_model("кг", 1)
    return nomenclature_model(name, full_name, group, unit, position_type.RAW_MATERIAL)


def test_valid_nomenclature_created_constructor_all_fields_are_set():
    """Валидное создание номенклатуры сохраняет все переданные поля."""
    nomenclature = _build_nomenclature()
    assert nomenclature.name == "Мука"
    assert nomenclature.full_name == "Мука пшеничная высший сорт"
    assert nomenclature.position_type == position_type.RAW_MATERIAL


def test_validation_exception_constructor_name_longer_than_50_raises():
    """Имя длиннее 50 символов вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        _build_nomenclature(name="Н" * 51)


def test_validation_exception_constructor_empty_name_raises():
    """Пустое имя вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        _build_nomenclature(name="")


def test_validation_exception_constructor_full_name_longer_than_255_raises():
    """Полное наименование длиннее 255 символов вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        _build_nomenclature(full_name="Н" * 256)


def test_validation_exception_constructor_empty_full_name_raises():
    """Пустое полное наименование вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        _build_nomenclature(full_name="")


def test_full_name_is_updated_full_name_setter_valid_value_accepted():
    """Сеттер full_name принимает значение длиннее 50 символов."""
    nomenclature = _build_nomenclature()
    long_value = "Мука пшеничная высшего сорта особого урожая, произведённая по ГОСТ"
    nomenclature.full_name = long_value
    assert nomenclature.full_name == long_value


def test_validation_exception_full_name_setter_invalid_value_raises():
    """Сеттер full_name бросает исключение валидации на невалидном значении."""
    nomenclature = _build_nomenclature()
    with pytest.raises(validation_exception):
        nomenclature.full_name = ""
