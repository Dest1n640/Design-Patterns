"""Юнит-тесты для Src.Dtos.table_dto.TableDto."""

import pytest

from Src.Core.exception import ValidationException
from Src.Dtos.table_dto import TableDto


def test_table_dto__valid_table__fields_are_set():
    """Заголовок, шапка и строки сохраняются; списки отдаются копиями."""
    table = TableDto("Мука", ["id", "name"], [["1", "Мука"]])

    table.rows[0].append("лишнее")

    assert table.title == "Мука"
    assert table.header == ["id", "name"]
    assert table.rows == [["1", "Мука"]]


def test_table_dto__row_length_mismatch__raises():
    """Строка другой длины, чем шапка, вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        TableDto("Мука", ["id", "name"], [["1"]])
