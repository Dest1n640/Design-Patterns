from Src.Dtos.table_dto import TableDto
from Src.Logics.Reports.table_report import TableReport


class TextReport(TableReport):
    """Текстовый отчёт: строки таблицы с разделителем « | »."""

    def _format(self, table: TableDto) -> str:
        """Оформляет таблицу строками « | »; переносы в ячейке заменяются пробелом."""
        return "\n".join(
            " | ".join(c.replace("\n", " ") for c in row)
            for row in [table.header, *table.rows]
        )
