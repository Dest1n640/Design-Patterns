from Src.Core.exception import ValidationException
from Src.Core.validation import Validation


class ReportModel:
    """Результат построения отчёта: либо текст, либо бинарные данные."""

    def __init__(self, name: str, text: str = "", binary: bytes = b"") -> None:
        """Конструктор отчёта: ровно одно из text и binary должно быть непустым."""
        self.__name = Validation.validate_string(name, "name")
        Validation.validate_instance(
            text, str, "text", "Текст отчёта должен быть строкой"
        )
        Validation.validate_instance(
            binary, bytes, "binary", "Бинарные данные отчёта должны быть bytes"
        )
        if bool(text.strip()) == bool(binary):
            raise ValidationException(
                "report", "Нужно задать ровно одно из: text или binary"
            )
        self.__text = text
        self.__binary = binary

    @property
    def name(self) -> str:
        """Возвращает наименование отчёта."""
        return self.__name

    @property
    def text(self) -> str:
        """Возвращает текстовое содержимое отчёта; пустая строка для бинарного."""
        return self.__text

    @property
    def binary(self) -> bytes:
        """Возвращает бинарное содержимое отчёта; пустые bytes для текстового."""
        return self.__binary
