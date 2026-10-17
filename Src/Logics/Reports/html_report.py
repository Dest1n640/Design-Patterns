from html import escape

from Src.Logics.Reports.table_report import Header, Row, TableReport


class HtmlReport(TableReport):
    """HTML-отчёт: таблица с именем сущности в заголовке."""

    def _format(self, title: str, header: Header, rows: list[Row]) -> str:
        """Оформляет таблицу в HTML; значения экранируются."""
        lines = [
            "<table>",
            f"<caption>{escape(title)}</caption>",
            self._row(header, "th"),
        ]
        lines += [self._row(row, "td") for row in rows]
        lines.append("</table>")
        return "\n".join(lines)

    @staticmethod
    def _row(cells: tuple, tag: str) -> str:
        """Оформляет строку таблицы из ячеек th или td."""
        row = "".join(f"<{tag}>{escape(str(c))}</{tag}>" for c in cells)
        return f"<tr>{row}</tr>"
