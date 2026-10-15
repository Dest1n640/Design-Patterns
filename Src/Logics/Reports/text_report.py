from Src.Core.abstract_report import AbstractReport
from Src.Core.validation import Validation
from Src.Dtos.report_model import ReportModel
from Src.Models.dish_model import DishModel


class TextReport(AbstractReport):
    """Текстовый отчёт по блюду: состав с весом брутто и нетто."""

    def build(self, source: DishModel) -> ReportModel:
        """Строит текстовый отчёт по составу блюда."""
        dish = Validation.validate_instance(
            source, DishModel, "source", "Источник отчёта должен быть блюдом"
        )
        lines = ["Код | Наименование | Брутто | Нетто"]
        for item in dish.ingredients:
            if isinstance(item, DishModel):
                brutto, netto = item.calculate_brutto(), item.calculate_netto()
            else:
                brutto, netto = item.brutto, item.netto
            lines.append(f"{item.id} | {item.name} | {brutto} | {netto}")
        return ReportModel(dish.name, text="\n".join(lines))
