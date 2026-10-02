import json
from abc import ABC, abstractmethod

from Src.Core.exception import ApplicationException
from Src.Core.validation import Validation


class AbstractManager(ABC):
    """Абстрактный базовый класс менеджеров: загрузка данных и их преобразование."""

    _DEFAULT_FILE_NAME: str = ""

    def __init__(self) -> None:
        """Инициализирует пустое состояние менеджера."""
        self._file_name: str = ""
        self._is_loaded: bool = False
        self._data: object = None

    def load(self, file_name: str = "") -> None:
        """Читает json-файл (по умолчанию _DEFAULT_FILE_NAME) и запускает convert."""
        self._is_loaded = False
        self._file_name = Validation.validate_string(
            file_name if file_name.strip() else self._DEFAULT_FILE_NAME, "file_name"
        )
        try:
            with open(self._file_name, encoding="utf-8") as file:
                self._data = json.load(file)
        except (OSError, ValueError) as ex:
            raise ApplicationException(
                f"Не удалось прочитать файл '{self._file_name}'"
            ) from ex
        self._is_loaded = self.convert()

    @abstractmethod
    def convert(self) -> bool:
        """Преобразует загруженные данные; возвращает True при успехе."""

    @property
    def is_loaded(self) -> bool:
        """Возвращает признак того, что данные успешно загружены и обработаны."""
        return self._is_loaded
