from abc import ABC, abstractmethod

from Src.Core.abstract_model import AbstractModel
from Src.Dtos.report_model import ReportModel


class AbstractReport(ABC):
    """Построитель отчёта: по исходной модели формирует результат."""

    @abstractmethod
    def build(self, source: AbstractModel) -> ReportModel:
        """Строит отчёт по исходной модели."""
