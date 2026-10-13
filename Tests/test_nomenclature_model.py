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


def test_nomenclature_model__constructor__name_of_50_chars_is_accepted():
    """Имя длиной ровно 50 символов допустимо."""
    _build_nomenclature(name="Н" * 50)


def test_nomenclature_model__constructor__name_longer_than_50_raises():
    """Имя длиннее 50 символов вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _build_nomenclature(name="Н" * 51)


def test_nomenclature_model__constructor__full_name_of_255_chars_is_accepted():
    """Полное наименование длиной ровно 255 символов допустимо."""
    _build_nomenclature(full_name="Н" * 255)


def test_nomenclature_model__constructor__full_name_longer_than_255_raises():
    """Полное наименование длиннее 255 символов вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        _build_nomenclature(full_name="Н" * 256)


def test_nomenclature_model__create_margherita__refers_to_passed_dictionaries():
    """Фабрика создаёт 9 позиций рецепта со ссылками на переданные справочники."""
    gram = MeasurementUnitModel.create_gram()
    units = {
        "грамм": gram,
        "килограмм": MeasurementUnitModel.create_kilogram(gram),
        "миллилитр": MeasurementUnitModel.create_milliliter(),
        "штука": MeasurementUnitModel.create_piece(),
    }
    names = ["Бакалея", "Молочные продукты", "Овощи", "Полуфабрикаты", "Блюда"]
    groups = {name: NomenclatureGroupModel(name) for name in names}

    positions = NomenclatureModel.create_margherita_nomenclature(groups, units)
    dough = {position.name: position for position in positions}["Тесто для пиццы"]

    assert len(positions) == 9
    assert dough.position_type is PositionType.SEMI_FINISHED
    assert dough.group is groups["Полуфабрикаты"]
    assert dough.measurement_unit is units["килограмм"]
