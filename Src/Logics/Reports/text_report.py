from Src.Logics.Reports.dish_report import DishReport, Row


class TextReport(DishReport):
    """Текстовый отчёт по блюду: состав с весом брутто и нетто."""

    def _format(self, title: str, rows: list[Row]) -> str:
        """Оформляет состав строками с разделителем « | »."""
        return "\n".join(" | ".join(map(str, row)) for row in [self.HEADER, *rows])
