import csv
import io

from Src.Dtos.table_dto import TableDto
from Src.Logics.Reports.table_report import TableReport


class CsvReport(TableReport):
    """CSV-отчёт: таблица с заголовком в виде байтов файла."""

    def _format(self, table: TableDto) -> bytes:
        """Оформляет таблицу в CSV; utf-8-sig, чтобы Excel прочитал кириллицу."""
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(table.header)
        writer.writerows(table.rows)
        return buffer.getvalue().encode("utf-8-sig")
