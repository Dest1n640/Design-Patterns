"""Юнит-тесты для конверторов Src.Logics.Convertors."""

from datetime import datetime

import pytest

from Src.Core.exception import ValidationException
from Src.Core.position_type import PositionType
from Src.Logics.convert_factory import ConvertFactory
from Src.Logics.Convertors.basic_convertor import BasicConvertor
from Src.Logics.Convertors.datetime_convertor import DatetimeConvertor
from Src.Logics.Convertors.enum_convertor import EnumConvertor
from Src.Logics.Convertors.reference_convertor import ReferenceConvertor
from Src.Models.nomenclature_model import NomenclatureModel
from Src.Models.technological_map_model import TechnologicalMapModel


class DatedStub:
    """Заглушка с датой: среди моделей пока нет свойств типа datetime."""

    @property
    def created(self) -> datetime:
        """Возвращает дату создания."""
        return datetime(2026, 10, 21, 12, 30)

    @property
    def name(self) -> str:
        """Возвращает имя."""
        return "заглушка"


@pytest.fixture
def flour(groups, units) -> NomenclatureModel:
    """Возвращает номенклатуру «Мука» со ссылками на группу и единицу измерения."""
    return NomenclatureModel(
        "Мука",
        "Мука пшеничная",
        groups["Бакалея"],
        units["килограмм"],
        PositionType.RAW_MATERIAL,
    )


def test_basic_convertor__unit_with_reference__numbers_and_strings_only(units):
    """Числа и строки попадают в словарь, ссылка на базовую единицу — нет."""
    kilogram = units["килограмм"]

    assert BasicConvertor().convert(kilogram) == {
        "base_coefficient": 1000,
        "coefficient": 1000,
        "id": kilogram.id,
        "name": "килограмм",
    }


def test_basic_convertor__composite_fields__skipped(flour):
    """Ссылки на сущности и enum пропускаются."""
    assert BasicConvertor().convert(flour) == {
        "full_name": "Мука пшеничная",
        "id": flour.id,
        "name": "Мука",
    }


def test_datetime_convertor__date_field__iso_string():
    """Дата попадает в словарь строкой ISO 8601, остальные свойства — нет."""
    assert DatetimeConvertor().convert(DatedStub()) == {
        "created": "2026-10-21T12:30:00"
    }


def test_datetime_convertor__no_dates__empty(flour):
    """У модели без дат получается пустой словарь."""
    assert DatetimeConvertor().convert(flour) == {}


def test_enum_convertor__enum_field__value(flour):
    """Enum попадает в словарь значением элемента, остальные свойства — нет."""
    assert EnumConvertor().convert(flour) == {"position_type": "raw_material"}


def test_enum_convertor__no_enums__empty(units):
    """У модели без Enum получается пустой словарь."""
    assert EnumConvertor().convert(units["килограмм"]) == {}


def test_reference_convertor__references__nested_dicts(flour, groups, units):
    """Ссылки на сущности вкладываются в словарь целиком, со всеми полями."""
    factory = ConvertFactory()

    assert ReferenceConvertor(factory.convert).convert(flour) == {
        "group": factory.convert(groups["Бакалея"]),
        "measurement_unit": factory.convert(units["килограмм"]),
    }


def test_reference_convertor__none_reference__skipped(units):
    """Пустая ссылка (base_unit=None) в словарь не попадает."""
    convertor = ReferenceConvertor(ConvertFactory().convert)

    assert convertor.convert(units["грамм"]) == {}


@pytest.mark.parametrize(
    "convertor",
    [
        BasicConvertor(),
        DatetimeConvertor(),
        EnumConvertor(),
        ReferenceConvertor(ConvertFactory().convert),
    ],
)
def test_convertor__none__raises(convertor):
    """None вместо объекта вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        convertor.convert(None)


def test_convert_factory__model__all_convertors_merged(units):
    """Словарь модели объединяет тип, простые поля и вложенные ссылки."""
    kilogram = units["килограмм"]

    assert ConvertFactory().convert(kilogram) == {
        "type": "MeasurementUnitModel",
        "base_coefficient": 1000,
        "base_unit": {
            "type": "MeasurementUnitModel",
            "base_coefficient": 1,
            "coefficient": 1,
            "id": units["грамм"].id,
            "name": "грамм",
        },
        "coefficient": 1000,
        "id": kilogram.id,
        "name": "килограмм",
    }


def test_convert_factory__datetime__merged():
    """Дата попадает в общий словарь вместе с простыми полями."""
    assert ConvertFactory().convert(DatedStub()) == {
        "type": "DatedStub",
        "created": "2026-10-21T12:30:00",
        "name": "заглушка",
    }


def test_convert_factory__list__list_of_dicts(units):
    """Список объектов превращается в список словарей в том же порядке."""
    result = ConvertFactory().convert(list(units.values()))

    assert [item["name"] for item in result] == list(units)


def test_convert_factory__dict__dict_of_dicts(units):
    """Словарь объектов превращается в словарь словарей с теми же ключами."""
    result = ConvertFactory().convert(units)

    assert {key: item["name"] for key, item in result.items()} == {
        key: unit.name for key, unit in units.items()
    }


def test_convert_factory__composite__structure_kept(groups, units):
    """Вложенные списки сохраняют структуру: карта → блюда → состав."""
    recipe = TechnologicalMapModel.create_technological_map(groups, units)

    factory = ConvertFactory()

    result = factory.convert(recipe)

    assert set(result) == {"type", "dishes", "id", "name"}
    dough, pizza = result["dishes"]
    assert set(dough) == {"type", "id", "ingredients", "name", "recipe"}
    assert pizza["ingredients"][0] == dough
    assert dough["ingredients"][0] == {
        "type": "IngredientModel",
        "brutto": 150,
        "full_name": "Мука пшеничная высшего сорта",
        "group": factory.convert(groups["Бакалея"]),
        "id": recipe.dishes[0].ingredients[0].id,
        "measurement_unit": factory.convert(units["грамм"]),
        "name": "Мука пшеничная",
        "netto": 150,
        "position_type": "raw_material",
    }


def test_convert_factory__none__raises():
    """None вместо объекта вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        ConvertFactory().convert(None)
