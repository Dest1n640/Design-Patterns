from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.common import Common
from Src.Logics.Convertors.basic_convertor import BasicConvertor
from Src.Logics.Convertors.datetime_convertor import DatetimeConvertor
from Src.Logics.Convertors.reference_convertor import ReferenceConvertor


class ConvertFactory:
    """Фабрика конверторов: собирает словари объекта из конверторов по типам полей."""

    def __init__(self) -> None:
        """Конструктор: регистрирует конверторы простых типов, дат и ссылок."""
        self.__convertors: list[AbstractConvertor] = [
            BasicConvertor(),
            DatetimeConvertor(),
            ReferenceConvertor(),
        ]

    def convert(self, source: object) -> dict | list:
        """Превращает объект в словарь, список — в список словарей."""
        if isinstance(source, list):
            return [self.convert(item) for item in source]
        result = {}
        for convertor in self.__convertors:
            for field, value in convertor.convert(source).items():
                result[field] = value
        for field in Common.get_fields(source):
            value = getattr(source, field)
            if isinstance(value, list):
                result[field] = self.convert(value)
        return result
