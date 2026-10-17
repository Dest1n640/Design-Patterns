from html import escape

from Src.Logics.Reports.dish_report import DishReport, Row


class HtmlReport(DishReport):
    """HTML-отчёт по блюду: таблица состава с названием блюда."""

    def _format(self, title: str, rows: list[Row]) -> str:
        """Оформляет состав в HTML-таблицу; значения экранируются."""
        lines = [
            "<table>",
            f"<caption>{escape(title)}</caption>",
            self._row(self.HEADER, "th"),
        ]
        lines += [self._row(row, "td") for row in rows]
        lines.append("</table>")
        return "\n".join(lines)

    @staticmethod
    def _row(cells: tuple, tag: str) -> str:
        """Оформляет строку таблицы из ячеек th или td."""
        row = "".join(f"<{tag}>{escape(str(c))}</{tag}>" for c in cells)
        return f"<tr>{row}</tr>"
