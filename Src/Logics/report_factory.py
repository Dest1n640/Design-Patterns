from Src.Core.abstract_factory import AbstractFactory
from Src.Core.abstract_report import AbstractReport
from Src.Core.exception import ValidationException
from Src.Core.report_type import ReportType
from Src.Core.validation import Validation
from Src.Logics.Reports.binary_report import BinaryReport
from Src.Logics.Reports.text_report import TextReport
from Src.Models.settings_model import SettingsModel


class ReportFactory(AbstractFactory):
    """Фабрика отчётов: сопоставляет тип отчёта его построителю."""

    def __init__(self, settings: SettingsModel) -> None:
        """Конструктор: запоминает настройки и регистрирует построители по типам."""
        self.__settings = Validation.validate_instance(
            settings, SettingsModel, "settings", "Настройки указаны некорректно"
        )
        self.__mapping: dict[ReportType, type[AbstractReport]] = {
            ReportType.TXT: TextReport,
            ReportType.BINARY: BinaryReport,
        }

    def create(self, report_type: ReportType) -> AbstractReport:
        """Создаёт построитель отчёта по типу; для нереализованного типа — ошибка."""
        report_type = Validation.validate_instance(
            report_type, ReportType, "report_type", "Тип отчёта указан некорректно"
        )
        if report_type not in self.__mapping:
            raise ValidationException(
                "report_type", f"Тип отчёта '{report_type.value}' не реализован"
            )
        return self.__mapping[report_type]()

    def create_default(self) -> AbstractReport:
        """Создаёт построитель отчёта по формату ответа из настроек."""
        return self.create(self.__settings.response_format)
