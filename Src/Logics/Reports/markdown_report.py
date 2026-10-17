from Src.Logics.Reports.dish_report import DishReport, Row


class MarkdownReport(DishReport):
    """Markdown-отчёт по блюду: заголовок и таблица состава."""

    def _format(self, title: str, rows: list[Row]) -> str:
        """Оформляет состав в Markdown-таблицу под заголовком с именем блюда."""
        lines = [
            f"# {title}",
            "",
            self._line(self.HEADER),
            self._line(["---"] * len(self.HEADER)),
        ]
        lines += [self._line(row) for row in rows]
        return "\n".join(lines)

    @staticmethod
    def _line(cells: tuple | list) -> str:
        """Оформляет строку таблицы; символ | в значении экранируется."""
        return "| " + " | ".join(str(c).replace("|", r"\|") for c in cells) + " |"
