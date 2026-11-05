"""Юнит-тесты конверторов десериализации отдельных типов полей."""

from datetime import datetime

import pytest

from Src.Core.exception import ValidationException
from Src.Core.position_type import PositionType
from Src.Core.report_type import ReportType
from Src.Logics.Convertors.basic_deserialize import BasicDeserialize
from Src.Logics.Convertors.collection_deserialize import CollectionDeserialize
from Src.Logics.Convertors.datetime_deserialize import DatetimeDeserialize
from Src.Logics.Convertors.enum_deserialize import EnumDeserialize
from Src.Logics.Convertors.reference_deserialize import ReferenceDeserialize
from Src.Logics.deserialize_factory import DeserializeFactory


def test_basic_deserialize__simple_and_nested_fields__simple_values_only():
    """Простые значения сохраняются, вложенные модели и коллекции пропускаются."""
    # Подготовка
    source = {
        "name": "грамм",
        "coefficient": 1,
        "enabled": True,
        "base_unit": None,
        "group": {"type": "NomenclatureGroupModel", "name": "Бакалея"},
        "items": [],
    }

    # Действия
    result = BasicDeserialize().convert(source)

    # Проверки
    assert result == {
        "name": "грамм",
        "coefficient": 1,
        "enabled": True,
        "base_unit": None,
    }


@pytest.mark.parametrize(
    ("enum_type", "member"),
    [(PositionType, member) for member in PositionType]
    + [(ReportType, member) for member in ReportType],
)
def test_enum_deserialize__serialized_member__enum_restored(enum_type, member):
    """Конвертор восстанавливает перечисление по значению, сохраняя обычные строки."""
    # Подготовка
    source = {"kind": member.value, "name": member.value}
    convertor = EnumDeserialize({"kind": enum_type, "name": str})

    # Действия
    result = convertor.convert(source)

    # Проверки
    assert result == {"kind": member}
    assert result["kind"] is member


@pytest.mark.parametrize("value", ["unknown", "RAW_MATERIAL", None, 42, [], {}])
def test_enum_deserialize__invalid_value__raises(value):
    """Ошибочное значение перечисления вызывает исключение с именем поля."""
    # Подготовка
    convertor = EnumDeserialize({"position_type": PositionType})
    source = {"position_type": value}

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        convertor.convert(source)

    # Проверки
    assert exc_info.value.field == "position_type"


@pytest.mark.parametrize(
    "value", ["2026-10-21T12:30:00", "2026-10-21T12:30:00.123456+08:00"]
)
def test_datetime_deserialize__iso_string__datetime_restored(value):
    """Строка ISO 8601 восстанавливается с сохранением точности и часового пояса."""
    # Подготовка
    convertor = DatetimeDeserialize({"created": datetime, "name": str})
    source = {"created": value, "name": value}

    # Действия
    result = convertor.convert(source)

    # Проверки
    assert result == {"created": datetime.fromisoformat(value)}
    assert isinstance(result["created"], datetime)


@pytest.mark.parametrize("value", ["not-a-date", None, 42, [], {}])
def test_datetime_deserialize__invalid_date__raises(value):
    """Ошибочная дата вызывает исключение валидации с именем поля."""
    # Подготовка
    convertor = DatetimeDeserialize({"created": datetime})
    source = {"created": value}

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        convertor.convert(source)

    # Проверки
    assert exc_info.value.field == "created"


@pytest.mark.parametrize(
    "convertor",
    [
        BasicDeserialize(),
        DatetimeDeserialize({"created": datetime}),
        EnumDeserialize({"position_type": PositionType}),
        ReferenceDeserialize(DeserializeFactory().convert),
        CollectionDeserialize(DeserializeFactory().convert),
    ],
)
def test_deserialize_convertor__invalid_source__raises(convertor):
    """Конверторы отклоняют None вместо словаря или коллекции."""
    # Подготовка
    source = None

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        convertor.convert(source)

    # Проверки
    assert exc_info.value.field == "source"
