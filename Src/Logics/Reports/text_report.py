from Src.Logics.Reports.table_report import Header, Row, TableReport


class TextReport(TableReport):
    """Текстовый отчёт: строки таблицы с разделителем « | »."""

    def _format(self, title: str, header: Header, rows: list[Row]) -> str:
        """Оформляет таблицу строками с разделителем « | »."""
        return "\n".join(" | ".join(map(str, row)) for row in [header, *rows])
