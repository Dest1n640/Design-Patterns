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
            ReferenceConvertor(self.convert),
        ]

    def convert(self, source: object) -> dict | list:
        """Превращает объект в словарь; списки и словари обходит рекурсивно."""
        if isinstance(source, list):
            return [self.convert(item) for item in source]
        if isinstance(source, dict):
            return {key: self.convert(item) for key, item in source.items()}
        # Имя класса нужно при загрузке: по нему выбирается, какую модель создать.
        result = {"type": type(source).__name__}
        for convertor in self.__convertors:
            for field, value in convertor.convert(source).items():
                result[field] = value
        for field in Common.get_fields(source):
            value = getattr(source, field)
            if isinstance(value, list | dict):
                result[field] = self.convert(value)
        return result
