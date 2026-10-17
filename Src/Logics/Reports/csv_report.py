import csv
import io

from Src.Logics.Reports.table_report import Header, Row, TableReport


class CsvReport(TableReport):
    """CSV-отчёт: таблица с заголовком в виде байтов файла."""

    def _format(self, title: str, header: Header, rows: list[Row]) -> bytes:
        """Оформляет таблицу в CSV; utf-8-sig, чтобы Excel прочитал кириллицу."""
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
        return buffer.getvalue().encode("utf-8-sig")
