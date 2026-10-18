"""Юнит-тесты для отчётов-наследников TableReport: CSV, Markdown, XML, HTML."""

import pytest

from Src.Core.exception import ValidationException
from Src.Logics.Reports.csv_report import CsvReport
from Src.Logics.Reports.html_report import HtmlReport
from Src.Logics.Reports.markdown_report import MarkdownReport
from Src.Logics.Reports.xml_report import XmlReport
from Src.Models.technological_map_model import TechnologicalMapModel

REPORTS = [CsvReport, MarkdownReport, XmlReport, HtmlReport]


@pytest.mark.parametrize(
    ("report", "expected"),
    [
        (CsvReport, "1000,грамм,1000,{id},килограмм"),
        (MarkdownReport, "| 1000 | грамм | 1000 | {id} | килограмм |"),
        (XmlReport, '<field name="base_unit">грамм</field>'),
        (
            HtmlReport,
            "<td>1000</td><td>грамм</td><td>1000</td><td>{id}</td><td>килограмм</td>",
        ),
    ],
)
def test_table_report__measurement_unit__row_in_format(report, expected, units):
    """Отчёт содержит строку единицы измерения в своём формате; имя — имя сущности."""
    kilogram = units["килограмм"]

    result = report().build(kilogram)
    content = result.text or result.binary.decode("utf-8-sig")

    assert result.name == "килограмм"
    assert expected.format(id=kilogram.id) in content


def test_markdown_report__recipe__multiline_cell_kept_in_table(groups, units):
    """Многострочный рецепт не разрывает Markdown-таблицу: переносы — <br>."""
    recipe = TechnologicalMapModel.create_technological_map(groups, units)

    lines = MarkdownReport().build(recipe).binary.decode("utf-8").split("\n")

    # Заголовок, пустая строка, шапка, разделитель и строка на каждое блюдо.
    assert len(lines) == 4 + len(recipe.dishes)
    assert "<br>2. " in lines[4]


@pytest.mark.parametrize(
    ("report", "is_binary"),
    [
        (CsvReport, True),
        (MarkdownReport, True),
        (XmlReport, False),
        (HtmlReport, False),
    ],
)
def test_table_report__build__csv_markdown_binary_others_text(report, is_binary, units):
    """CSV и Markdown отдают байты файла, XML и HTML — текст."""
    result = report().build(units["грамм"])

    assert bool(result.binary) is is_binary
    assert bool(result.text) is not is_binary


@pytest.mark.parametrize("report", REPORTS)
def test_table_report__build__not_a_model_raises(report):
    """Источник, не являющийся сущностью, вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        report().build("не модель")
