from Src.Dtos.table_dto import TableDto
from Src.Logics.Reports.table_report import TableReport


class MarkdownReport(TableReport):
    """Markdown-отчёт: заголовок с именем сущности и таблица в виде байтов файла."""

    def _format(self, table: TableDto) -> bytes:
        """Оформляет таблицу в Markdown под заголовком с именем сущности."""
        lines = [
            f"# {table.title}",
            "",
            self._line(table.header),
            self._line(["---"] * len(table.header)),
        ]
        lines += [self._line(row) for row in table.rows]
        return "\n".join(lines).encode("utf-8")

    @staticmethod
    def _line(cells: list[str]) -> str:
        """Оформляет строку таблицы; | экранируется, перенос строки — <br>."""
        cells = [c.replace("|", r"\|").replace("\n", "<br>") for c in cells]
        return "| " + " | ".join(cells) + " |"
