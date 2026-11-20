from typing import Self

from Src.Core.abstract_model import AbstractModel
from Src.Core.filter_type import FilterType
from Src.Dtos.filter_dto import FilterDto, FilterItem


class FilterPrototype[Model: AbstractModel]:
    """Хранит выборку доменных объектов и создаёт новые выборки по фильтру."""

    def __init__(self, data) -> None:
        """Сохраняет отдельный список исходных объектов."""
        self._data = list(data)

    @property
    def data(self) -> list[Model]:
        """Возвращает копию списка объектов текущей выборки."""
        return self._data.copy()

    def clone[Item: FilterItem](self, filter_dto: FilterDto[Item]) -> Self:
        """Создаёт прототип с объектами, которые подходят под все условия."""
        conditions = [(item.field.split("."), item) for item in filter_dto.filters]
        matches = (
            model
            for model in self._data
            if all(_matches(model, path, item) for path, item in conditions)
        )
        return type(self)(matches)


def _matches(model: AbstractModel, path: list[str], item: FilterItem) -> bool:
    """Проверяет, подходит ли хотя бы одно строковое значение по пути."""
    values = _field_values(model, path)
    if item.filter_type is FilterType.EQUALS:
        return item.value in values

    expected = item.value.casefold()
    return any(expected in value.casefold() for value in values)


def _field_values(source: object, path: list[str]):
    """Читает строковые значения по пути, проходя через объекты и списки."""
    if isinstance(source, list):
        for item in source:
            yield from _field_values(item, path)
    elif path and source is not None:
        yield from _field_values(getattr(source, path[0], None), path[1:])
    elif isinstance(source, str):
        yield source
