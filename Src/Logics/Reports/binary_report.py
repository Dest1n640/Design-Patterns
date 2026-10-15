import pickle

from Src.Core.abstract_report import AbstractReport
from Src.Core.validation import Validation
from Src.Dtos.report_model import ReportModel
from Src.Models.dish_model import DishModel


class BinaryReport(AbstractReport):
    """Бинарный отчёт по блюду: модель блюда, сериализованная pickle."""

    def build(self, source: DishModel) -> ReportModel:
        """Сериализует блюдо со всеми ингредиентами в байты."""
        dish = Validation.validate_instance(
            source, DishModel, "source", "Источник отчёта должен быть блюдом"
        )
        return ReportModel(dish.name, binary=pickle.dumps(dish))
