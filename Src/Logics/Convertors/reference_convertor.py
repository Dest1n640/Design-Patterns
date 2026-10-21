from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.abstract_model import AbstractModel
from Src.Core.common import Common


class ReferenceConvertor(AbstractConvertor):
    """Конвертор ссылок: в словарь попадают свойства-сущности в виде их id."""

    def convert(self, source: object) -> dict:
        """Возвращает словарь «наименование свойства → id связанной сущности»."""
        result = {}
        for field in Common.get_fields(source):
            value = getattr(source, field)
            if isinstance(value, AbstractModel):
                result[field] = value.id
        return result
