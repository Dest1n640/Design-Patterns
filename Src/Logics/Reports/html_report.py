from html import escape

from Src.Dtos.table_dto import TableDto
from Src.Logics.Reports.table_report import TableReport


class HtmlReport(TableReport):
    """HTML-отчёт: таблица с именем сущности в заголовке."""

    def _format(self, table: TableDto) -> str:
        """Оформляет таблицу в HTML; значения экранируются."""
        lines = [
            "<table>",
            f"<caption>{escape(table.title)}</caption>",
            self._row(table.header, "th"),
        ]
        lines += [self._row(row, "td") for row in table.rows]
        lines.append("</table>")
        return "\n".join(lines)

    @staticmethod
    def _row(cells: list[str], tag: str) -> str:
        """Оформляет строку таблицы из ячеек th или td."""
        row = "".join(f"<{tag}>{escape(c)}</{tag}>" for c in cells)
        return f"<tr>{row}</tr>"
