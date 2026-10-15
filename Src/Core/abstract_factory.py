from abc import ABC, abstractmethod

from Src.Core.abstract_report import AbstractReport
from Src.Core.report_type import ReportType


class AbstractFactory(ABC):
    """Фабрика отчётов: по типу отчёта возвращает построитель."""

    @abstractmethod
    def create(self, report_type: ReportType) -> AbstractReport:
        """Создаёт построитель отчёта указанного типа."""
