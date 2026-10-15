"""Юнит-тесты для Src.Logics.report_factory.ReportFactory."""

import pytest

from Src.Core.exception import ValidationException
from Src.Core.report_type import ReportType
from Src.Logics.report_factory import ReportFactory
from Src.Logics.Reports.binary_report import BinaryReport
from Src.Logics.Reports.text_report import TextReport


@pytest.mark.parametrize(
    ("report_type", "expected"),
    [(ReportType.TXT, TextReport), (ReportType.BINARY, BinaryReport)],
)
def test_report_factory__create__returns_report_for_type(report_type, expected):
    """По типу отчёта создаётся экземпляр соответствующего построителя."""
    assert isinstance(ReportFactory().create(report_type), expected)


def test_report_factory__create__not_a_report_type_raises():
    """Строка вместо ReportType вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        ReportFactory().create("txt")
