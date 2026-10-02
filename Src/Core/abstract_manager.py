import json
from abc import ABC, abstractmethod
from pathlib import Path

from Src.Core.exception import ApplicationException
from Src.Core.validation import Validation


class AbstractManager(ABC):
    """Абстрактный базовый класс менеджеров: загрузка данных и их преобразование."""

    _PROJECT_ROOT = Path(__file__).resolve().parents[2]
    _DEFAULT_FILE_NAME: str = ""

    def __init__(self) -> None:
        """Инициализирует пустое состояние менеджера."""
        self._file_name: str = ""
        self._is_loaded: bool = False
        self._data: object = None

    def load(self, file_name: str = "") -> None:
        """Читает json-файл (по умолчанию — из корня проекта) и запускает convert."""
        # Файл по умолчанию ищется от корня проекта, а не от текущего каталога.
        if isinstance(file_name, str) and not file_name.strip():
            file_name = str(self._PROJECT_ROOT / self._DEFAULT_FILE_NAME)
        file_name = Validation.validate_string(file_name, "file_name")
        try:
            with open(file_name, encoding="utf-8") as file:
                self._data = json.load(file)
        except (OSError, ValueError) as ex:
            raise ApplicationException(
                f"Не удалось прочитать файл '{file_name}'"
            ) from ex
        # При ошибке остаются признак и имя файла прошлой успешной загрузки.
        if self.convert():
            self._file_name = file_name
            self._is_loaded = True

    @abstractmethod
    def convert(self) -> bool:
        """Преобразует загруженные данные; возвращает True при успехе."""

    @property
    def is_loaded(self) -> bool:
        """Возвращает признак того, что данные успешно загружены и обработаны."""
        return self._is_loaded
