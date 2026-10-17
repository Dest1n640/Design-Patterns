"""Юнит-тесты для отчётов-наследников TableReport: CSV, Markdown, XML, HTML."""

import pytest

from Src.Core.exception import ValidationException
from Src.Logics.Reports.csv_report import CsvReport
from Src.Logics.Reports.html_report import HtmlReport
from Src.Logics.Reports.markdown_report import MarkdownReport
from Src.Logics.Reports.xml_report import XmlReport
from Src.Models.dish_model import DishModel

REPORTS = [CsvReport, MarkdownReport, XmlReport, HtmlReport]


@pytest.mark.parametrize(
    ("report", "expected_row"),
    [
        (CsvReport, "{id},Мука пшеничная,150,150"),
        (MarkdownReport, "| {id} | Мука пшеничная | 150 | 150 |"),
        (XmlReport, '<field name="Наименование">Мука пшеничная</field>'),
        (HtmlReport, "<td>{id}</td><td>Мука пшеничная</td><td>150</td><td>150</td>"),
    ],
)
def test_table_report__build__contains_ingredient_row(
    report, expected_row, groups, units
):
    """Отчёт содержит строку ингредиента в своём формате; имя отчёта — имя блюда."""
    dough, _ = DishModel.create_margherita_dishes(groups, units)
    flour = dough.ingredients[0]

    result = report().build(dough)
    content = result.text or result.binary.decode("utf-8-sig")

    assert result.name == dough.name
    assert expected_row.format(id=flour.id) in content


@pytest.mark.parametrize(
    ("report", "is_binary"),
    [
        (CsvReport, True),
        (MarkdownReport, True),
        (XmlReport, False),
        (HtmlReport, False),
    ],
)
def test_table_report__build__csv_markdown_binary_others_text(
    report, is_binary, groups, units
):
    """CSV и Markdown отдают байты файла, XML и HTML — текст."""
    dough, _ = DishModel.create_margherita_dishes(groups, units)

    result = report().build(dough)

    assert bool(result.binary) is is_binary
    assert bool(result.text) is not is_binary


@pytest.mark.parametrize("report", REPORTS)
def test_table_report__build__not_supported_source_raises(report):
    """Источник неподдерживаемого типа вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        report().build("не блюдо")
