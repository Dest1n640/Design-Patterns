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


def test_ValidNomenclatureCreated_Constructor_AllFieldsAreSet():
    """Валидное создание номенклатуры сохраняет все переданные поля."""
    nomenclature = _build_nomenclature()
    assert nomenclature.name == "Мука"
    assert nomenclature.full_name == "Мука пшеничная высший сорт"
    assert nomenclature.position_type == position_type.RAW_MATERIAL


def test_ValidationException_Constructor_NameLongerThan50Raises():
    """Имя длиннее 50 символов вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        _build_nomenclature(name="Н" * 51)


def test_ValidationException_Constructor_EmptyNameRaises():
    """Пустое имя вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        _build_nomenclature(name="")


def test_ValidationException_Constructor_FullNameLongerThan255Raises():
    """Полное наименование длиннее 255 символов вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        _build_nomenclature(full_name="Н" * 256)


def test_ValidationException_Constructor_EmptyFullNameRaises():
    """Пустое полное наименование вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        _build_nomenclature(full_name="")


def test_FullNameIsUpdated_FullNameSetter_ValidValueAccepted():
    """Сеттер full_name принимает значение длиннее 50 символов."""
    nomenclature = _build_nomenclature()
    long_value = "Мука пшеничная высшего сорта особого урожая, произведённая по ГОСТ"
    nomenclature.full_name = long_value
    assert nomenclature.full_name == long_value


def test_ValidationException_FullNameSetter_InvalidValueRaises():
    """Сеттер full_name бросает исключение валидации на невалидном значении."""
    nomenclature = _build_nomenclature()
    with pytest.raises(validation_exception):
        nomenclature.full_name = ""
