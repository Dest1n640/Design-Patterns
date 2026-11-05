from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.common import Common


class BasicConvertor(AbstractConvertor):
    """Конвертор простых типов: числовые, строковые и пустые (None) свойства."""

    def convert(self, source: object) -> dict:
        """Возвращает словарь «наименование свойства → значение» по простым типам."""
        result = {}
        for field in Common.get_fields(source):
            value = getattr(source, field)
            if isinstance(value, int | float | str | None):
                result[field] = value
        return result
