from Src.Core.exception import ValidationException
from Src.Core.validation import Validation


class TableDto:
    """Табличные данные отчёта: заголовок, шапка и строки значений."""

    def __init__(self, title: str, header: list[str], rows: list[list[str]]) -> None:
        """Конструктор таблицы: длина каждой строки должна совпадать с шапкой."""
        self.__title = Validation.validate_string(title, "title")
        self.__header = Validation.validate_instance(
            header, list, "header", "Шапка таблицы должна быть списком"
        )
        self.__rows = Validation.validate_instance(
            rows, list, "rows", "Строки таблицы должны быть списком"
        )
        if any(len(row) != len(header) for row in rows):
            raise ValidationException("rows", "Длина строки не совпадает с шапкой")

    @property
    def title(self) -> str:
        """Возвращает заголовок таблицы — имя сущности отчёта."""
        return self.__title

    @property
    def header(self) -> list[str]:
        """Возвращает шапку таблицы — имена колонок."""
        return list(self.__header)

    @property
    def rows(self) -> list[list[str]]:
        """Возвращает строки таблицы — значения в порядке колонок шапки."""
        return [list(row) for row in self.__rows]
