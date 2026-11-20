from Src.Dtos.filter_dto import FilterDto, FilterItem


class RecipeFilterItem(FilterItem):
    """Одно условие поиска по техкарте, её блюду или ингредиенту."""

    _nested_fields = (
        "dishes.name",
        "dishes.id",
        "dishes.ingredients.name",
        "dishes.ingredients.id",
    )


class RecipeFilterDto(FilterDto[RecipeFilterItem]):
    """Передаёт список условий поиска по рецептам."""
