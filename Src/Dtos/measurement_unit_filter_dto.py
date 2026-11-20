from Src.Dtos.filter_dto import FilterDto, FilterItem


class MeasurementUnitFilterItem(FilterItem):
    """Одно условие поиска по единице измерения или её базовой единице."""

    _nested_fields = ("base_unit.name", "base_unit.id")


class MeasurementUnitFilterDto(FilterDto[MeasurementUnitFilterItem]):
    """Передаёт список условий поиска по единицам измерения."""
