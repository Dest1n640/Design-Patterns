class application_exception(Exception):
    """Базовое исключение приложения. Общий предок для всех доменных исключений."""

    def __init__(self, message: str) -> None:
        """
        Инициализирует базовое исключение.

        :message: описание причины ошибки
        """
        super().__init__(message)
        self.__message = message

    @property
    def message(self) -> str:
        """Возвращает описание причины ошибки."""
        return self.__message


class validation_exception(application_exception):
    """Исключение, сигнализирующее о некорректном значении поля или аргумента."""

    def __init__(self, field: str, message: str) -> None:
        """
        Инициализирует исключение валидации.

        :field: наименование поля/аргумента, вызвавшего ошибку
        :message: описание, почему значение некорректно
        """
        super().__init__(message)
        self.__field = field

    @property
    def field(self) -> str:
        """Возвращает наименование некорректного поля."""
        return self.__field

    def __str__(self) -> str:
        """Строковое представление для логов и вывода в консоль."""
        return f"Ошибка валидации поля '{self.__field}': {self.message}"
