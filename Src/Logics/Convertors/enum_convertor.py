from enum import Enum

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.common import Common


class EnumConvertor(AbstractConvertor):
    """Конвертор перечислений: в словарь попадают только свойства типа Enum."""

    def convert(self, source: object) -> dict:
        """Возвращает словарь «наименование свойства → значение элемента Enum»."""
        result = {}
        for field in Common.get_fields(source):
            value = getattr(source, field)
            if isinstance(value, Enum):
                result[field] = value.value
        return result
