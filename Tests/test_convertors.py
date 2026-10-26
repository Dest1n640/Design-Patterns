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
    # Подготовка
    kilogram = units["килограмм"]

    # Действие
    result = BasicConvertor().convert(kilogram)

    # Проверки
    assert result == {
        "base_coefficient": 1000,
        "coefficient": 1000,
        "id": kilogram.id,
        "name": "килограмм",
    }


def test_basic_convertor__composite_fields__skipped(flour):
    """Ссылки на сущности и enum пропускаются."""
    # Действие
    result = BasicConvertor().convert(flour)

    # Проверки
    assert result == {
        "full_name": "Мука пшеничная",
        "id": flour.id,
        "name": "Мука",
    }


def test_datetime_convertor__date_field__iso_string():
    """Дата попадает в словарь строкой ISO 8601, остальные свойства — нет."""
    # Действие
    result = DatetimeConvertor().convert(DatedStub())

    # Проверки
    assert result == {"created": "2026-10-21T12:30:00"}


def test_datetime_convertor__no_dates__empty(flour):
    """У модели без дат получается пустой словарь."""
    # Действие
    result = DatetimeConvertor().convert(flour)

    # Проверки
    assert result == {}


def test_enum_convertor__enum_field__value(flour):
    """Enum попадает в словарь значением элемента, остальные свойства — нет."""
    # Действие
    result = EnumConvertor().convert(flour)

    # Проверки
    assert result == {"position_type": "raw_material"}


def test_enum_convertor__no_enums__empty(units):
    """У модели без Enum получается пустой словарь."""
    # Действие
    result = EnumConvertor().convert(units["килограмм"])

    # Проверки
    assert result == {}


def test_reference_convertor__references__nested_dicts(flour, groups, units):
    """Ссылки на сущности вкладываются в словарь целиком, со всеми полями."""
    # Подготовка
    factory = ConvertFactory()
    convertor = ReferenceConvertor(factory.convert)

    # Действие
    result = convertor.convert(flour)

    # Проверки
    assert result == {
        "group": factory.convert(groups["Бакалея"]),
        "measurement_unit": factory.convert(units["килограмм"]),
    }


def test_reference_convertor__none_reference__skipped(units):
    """Пустая ссылка (base_unit=None) в словарь не попадает."""
    # Подготовка
    convertor = ReferenceConvertor(ConvertFactory().convert)

    # Действие
    result = convertor.convert(units["грамм"])

    # Проверки
    assert result == {}


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
    # Действие и проверки
    with pytest.raises(ValidationException):
        convertor.convert(None)


def test_convert_factory__model__all_convertors_merged(units):
    """Словарь модели объединяет тип, простые поля и вложенные ссылки."""
    # Подготовка
    kilogram = units["килограмм"]

    # Действие
    result = ConvertFactory().convert(kilogram)

    # Проверки
    assert result == {
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
    # Действие
    result = ConvertFactory().convert(DatedStub())

    # Проверки
    assert result == {
        "type": "DatedStub",
        "created": "2026-10-21T12:30:00",
        "name": "заглушка",
    }


def test_convert_factory__list__list_of_dicts(units):
    """Список объектов превращается в список словарей в том же порядке."""
    # Действие
    result = ConvertFactory().convert(list(units.values()))

    # Проверки
    assert [item["name"] for item in result] == list(units)


def test_convert_factory__dict__dict_of_dicts(units):
    """Словарь объектов превращается в словарь словарей с теми же ключами."""
    # Действие
    result = ConvertFactory().convert(units)

    # Проверки
    assert {key: item["name"] for key, item in result.items()} == {
        key: unit.name for key, unit in units.items()
    }


def test_convert_factory__composite__structure_kept(groups, units):
    """Вложенные списки сохраняют структуру: карта → блюда → состав."""
    # Подготовка
    recipe = TechnologicalMapModel.create_technological_map(groups, units)
    factory = ConvertFactory()

    # Действие
    result = factory.convert(recipe)

    # Проверки
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
    # Действие и проверки
    with pytest.raises(ValidationException):
        ConvertFactory().convert(None)
