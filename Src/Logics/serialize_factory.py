from Src.Core.abstract_convertor import AbstractConvertor
from Src.Logics.Convertors.basic_serialize import BasicSerialize
from Src.Logics.Convertors.collection_serialize import CollectionSerialize
from Src.Logics.Convertors.datetime_serialize import DatetimeSerialize
from Src.Logics.Convertors.enum_serialize import EnumSerialize
from Src.Logics.Convertors.reference_serialize import ReferenceSerialize


class SerializeFactory(AbstractConvertor):
    """Фабрика конверторов: собирает словари объекта из конверторов по типам полей."""

    def __init__(self) -> None:
        """Регистрирует конверторы простых типов, дат, Enum, ссылок и коллекций."""
        self.__convertors: list[AbstractConvertor] = [
            BasicSerialize(),
            DatetimeSerialize(),
            EnumSerialize(),
            ReferenceSerialize(self.convert),
            CollectionSerialize(self.convert),
        ]

    def convert(self, source: object) -> dict | list:
        """Превращает объект в словарь; списки и словари обходит рекурсивно."""
        if isinstance(source, list | dict):
            return CollectionSerialize(self.convert).convert(source)
        # Имя класса нужно при загрузке: по нему выбирается, какую модель создать.
        result = {"type": type(source).__name__}
        for convertor in self.__convertors:
            result.update(convertor.convert(source))
        return result
