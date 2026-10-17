"""Юнит-тесты для Src.Logics.report_factory.ReportFactory."""

import pytest

from Src.Core.exception import ValidationException
from Src.Core.report_type import ReportType
from Src.Logics.report_factory import ReportFactory
from Src.Logics.Reports.csv_report import CsvReport
from Src.Logics.Reports.html_report import HtmlReport
from Src.Logics.Reports.markdown_report import MarkdownReport
from Src.Logics.Reports.text_report import TextReport
from Src.Logics.Reports.xml_report import XmlReport
from Src.Models.settings_model import SettingsModel


@pytest.mark.parametrize(
    ("report_type", "expected"),
    [
        (ReportType.TXT, TextReport),
        (ReportType.CSV, CsvReport),
        (ReportType.MARKDOWN, MarkdownReport),
        (ReportType.XML, XmlReport),
        (ReportType.HTML, HtmlReport),
    ],
)
def test_report_factory__create__returns_report_for_type(report_type, expected):
    """По типу отчёта создаётся экземпляр соответствующего построителя."""
    assert isinstance(ReportFactory(SettingsModel()).create(report_type), expected)


def test_report_factory__create__not_a_report_type_raises():
    """Строка вместо ReportType вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        ReportFactory(SettingsModel()).create("txt")


@pytest.mark.parametrize(
    ("response_format", "expected"),
    [(ReportType.TXT, TextReport), (ReportType.CSV, CsvReport)],
)
def test_report_factory__create_default__uses_settings_format(
    response_format, expected
):
    """create_default создаёт построитель по формату ответа из настроек."""
    settings = SettingsModel()
    settings.response_format = response_format
    assert isinstance(ReportFactory(settings).create_default(), expected)


def test_report_factory__constructor_not_settings__raises():
    """Не модель настроек в конструкторе вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        ReportFactory(None)
