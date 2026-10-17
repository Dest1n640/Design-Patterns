import csv
import io

from Src.Logics.Reports.table_report import Header, Row, TableReport


class CsvReport(TableReport):
    """CSV-отчёт: таблица с заголовком."""

    def _format(self, title: str, header: Header, rows: list[Row]) -> str:
        """Оформляет таблицу в CSV с заголовком."""
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
        return buffer.getvalue()
