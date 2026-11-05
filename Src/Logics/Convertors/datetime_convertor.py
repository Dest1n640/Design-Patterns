from datetime import datetime

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.common import Common


class DatetimeConvertor(AbstractConvertor):
    """Конвертор дат: в словарь попадают только свойства типа datetime."""

    def convert(self, source: object) -> dict:
        """Возвращает словарь «наименование свойства → дата в ISO 8601»."""
        result = {}
        for field in Common.get_fields(source):
            value = getattr(source, field)
            if isinstance(value, datetime):
                result[field] = value.isoformat()
        return result
