import csv
import io

from Src.Logics.Reports.dish_report import DishReport, Row


class CsvReport(DishReport):
    """CSV-отчёт по блюду: состав с весом брутто и нетто."""

    def _format(self, title: str, rows: list[Row]) -> str:
        """Оформляет состав в CSV с заголовком."""
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(self.HEADER)
        writer.writerows(rows)
        return buffer.getvalue()
