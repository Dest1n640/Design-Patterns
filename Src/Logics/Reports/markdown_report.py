from Src.Logics.Reports.table_report import Header, Row, TableReport


class MarkdownReport(TableReport):
    """Markdown-отчёт: заголовок с именем сущности и таблица."""

    def _format(self, title: str, header: Header, rows: list[Row]) -> str:
        """Оформляет таблицу в Markdown под заголовком с именем сущности."""
        lines = [
            f"# {title}",
            "",
            self._line(header),
            self._line(["---"] * len(header)),
        ]
        lines += [self._line(row) for row in rows]
        return "\n".join(lines)

    @staticmethod
    def _line(cells: tuple | list) -> str:
        """Оформляет строку таблицы; символ | в значении экранируется."""
        return "| " + " | ".join(str(c).replace("|", r"\|") for c in cells) + " |"
