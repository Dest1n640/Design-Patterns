from Src.Dtos.filter_dto import FilterDto, FilterItem


class NomenclatureFilterItem(FilterItem):
    """Одно условие поиска по полю номенклатуры или связанной модели."""

    _nested_fields = (
        "group.name",
        "group.id",
        "measurement_unit.name",
        "measurement_unit.id",
        "measurement_unit.base_unit.name",
        "measurement_unit.base_unit.id",
    )


class NomenclatureFilterDto(FilterDto[NomenclatureFilterItem]):
    """Передаёт список условий поиска по номенклатуре."""
