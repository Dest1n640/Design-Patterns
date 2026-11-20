from typing import ClassVar

from pydantic import BaseModel, field_validator

from Src.Core.filter_type import FilterType


class FilterItem(BaseModel):
    """Задаёт поле, оператор и строковое значение для одного условия."""

    _nested_fields: ClassVar[tuple[str, ...]] = ()

    field: str
    filter_type: FilterType
    value: str

    @field_validator("field")
    @classmethod
    def validate_field(cls, field: str) -> str:
        """Проверяет, что поле разрешено для выбранной модели."""
        if field not in ("name", "id") and field not in cls._nested_fields:
            raise ValueError(f"Поле «{field}» недоступно для фильтрации")
        return field


class FilterDto[Item: FilterItem](BaseModel):
    """Передаёт список условий фильтрации."""

    filters: list[Item]
