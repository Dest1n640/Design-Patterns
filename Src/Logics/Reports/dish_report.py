from abc import abstractmethod

from Src.Core.abstract_report import AbstractReport
from Src.Core.validation import Validation
from Src.Dtos.report_model import ReportModel
from Src.Models.dish_model import DishModel

type Row = tuple[str, str, int | float, int | float]


class DishReport(AbstractReport):
    """Основа отчётов по составу блюда: строки с кодом, именем, брутто и нетто."""

    HEADER = ("Код", "Наименование", "Брутто", "Нетто")

    def build(self, source: DishModel) -> ReportModel:
        """Строит отчёт по составу блюда в формате наследника."""
        dish = Validation.validate_instance(
            source, DishModel, "source", "Источник отчёта должен быть блюдом"
        )
        return ReportModel(dish.name, text=self._format(dish.name, self._rows(dish)))

    @staticmethod
    def _rows(dish: DishModel) -> list[Row]:
        """Возвращает строки состава; вес вложенного блюда считается суммарно."""
        rows = []
        for item in dish.ingredients:
            if isinstance(item, DishModel):
                brutto, netto = item.calculate_brutto(), item.calculate_netto()
            else:
                brutto, netto = item.brutto, item.netto
            rows.append((item.id, item.name, brutto, netto))
        return rows

    @abstractmethod
    def _format(self, title: str, rows: list[Row]) -> str:
        """Оформляет строки состава в текст нужного формата."""
