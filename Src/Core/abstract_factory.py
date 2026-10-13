from Src.Core.abstract_report import AbstractReport
from Core.report_type import ReportType
from abc import ABC, abstractmethod

class abstract_factory(ABC):

  @abstractmethod
  def create(self, report_type: ReportType) -> AbstractReport:
