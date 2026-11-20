from enum import Enum


class FilterType(Enum):
    """Способ сравнения значения поля при фильтрации."""

    EQUALS = "EQUALS"
    LIKE = "LIKE"
