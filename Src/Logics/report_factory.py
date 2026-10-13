from Src.Core.abstract_factory import abstract_factory
from Src.Core.abstract_report import AbstractReport
from Src.Core.report_type import ReportType
from Src.Logics.text_report import TextReport

class report_factory(AbstractReport):
  __mapping: dict[ReportType, abstract_factory]

  def __init__(self):
    self.__mapping[ReportType.TXT] = TextReport

  def create(report_type: ReportType) -> AbstractReport:
    if report_type not in self.__mapping.keys:
      raise ValueError(f"Указанный тип отчета {report_type}, не реализован")

    return self.__mapping[report_type]
