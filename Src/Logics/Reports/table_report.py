from abc import abstractmethod
from enum import Enum

from Src.Core.abstract_report import AbstractReport
from Src.Core.common import Common
from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation
from Src.Dtos.report_model import ReportModel
from Src.Dtos.table_dto import TableDto


class TableReport(AbstractReport):
    """Основа табличных отчётов: таблица сущности собирается рефлексией."""

    def build(self, source: NamedModel) -> ReportModel:
        """Строит отчёт по сущности в формате наследника: текст или байты."""
        source = Validation.validate_instance(
            source, NamedModel, "source", "Источник отчёта должен быть сущностью"
        )
        content = self._format(self._table(source))
        if isinstance(content, bytes):
            return ReportModel(source.name, binary=content)
        return ReportModel(source.name, text=content)

    @classmethod
    def _table(cls, source: NamedModel) -> TableDto:
        """Собирает таблицу: колонки — свойства моделей, строки — сами модели."""
        items = cls._items(source)
        header = []
        for item in items:
            header += [f for f in Common.get_fields(item, True) if f not in header]
        rows = [[cls._cell(getattr(item, f, None)) for f in header] for item in items]
        return TableDto(source.name, header, rows)

    @staticmethod
    def _items(source: NamedModel) -> list:
        """Возвращает элементы первого непустого списка, иначе саму сущность."""
        for field in Common.get_fields(source):
            value = getattr(source, field)
            if isinstance(value, list) and value:
                return value
        return [source]

    @staticmethod
    def _cell(value: object) -> str:
        """Приводит значение свойства к строке: модель — имя, enum — значение."""
        if value is None:
            return ""
        if isinstance(value, NamedModel):
            return value.name
        if isinstance(value, Enum):
            return str(value.value)
        return str(value)

    @abstractmethod
    def _format(self, table: TableDto) -> str | bytes:
        """Оформляет таблицу в текст или байты нужного формата."""
