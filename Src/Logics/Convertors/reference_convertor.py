from collections.abc import Callable

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.abstract_model import AbstractModel
from Src.Core.common import Common


class ReferenceConvertor(AbstractConvertor):
    """Конвертор ссылок: свойства-сущности вкладываются в словарь целиком."""

    def __init__(self, convert: Callable[[object], dict]) -> None:
        """Конструктор: convert — метод фабрики, строящий полный словарь сущности."""
        self.__convert = convert

    def convert(self, source: object) -> dict:
        """Возвращает словарь «наименование свойства → словарь связанной сущности»."""
        result = {}
        for field in Common.get_fields(source):
            value = getattr(source, field)
            # Глубокая сериализация: вместо id — все поля сущности, рекурсивно.
            if isinstance(value, AbstractModel):
                result[field] = self.__convert(value)
        return result
