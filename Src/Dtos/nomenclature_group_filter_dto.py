from Src.Dtos.filter_dto import FilterDto, FilterItem


class NomenclatureGroupFilterItem(FilterItem):
    """Одно условие поиска по наименованию или коду группы."""


class NomenclatureGroupFilterDto(FilterDto[NomenclatureGroupFilterItem]):
    """Передаёт список условий поиска по группам номенклатуры."""
