from abc import ABC, abstractmethod


class AbstractManager(ABC):
    """Абстрактный базовый класс менеджеров: загрузка данных и их преобразование."""

    def __init__(self) -> None:
        """Инициализирует пустое состояние менеджера."""
        self._file_name: str = ""
        self._is_loaded: bool = False
        self._data: object = None

    @abstractmethod
    def load(self, file_name: str = "") -> None:
        """Загружает данные и запускает их обработку через convert."""

    @abstractmethod
    def convert(self) -> bool:
        """Преобразует загруженные данные; возвращает True при успехе."""

    @property
    def is_loaded(self) -> bool:
        """Возвращает признак того, что данные успешно загружены и обработаны."""
        return self._is_loaded
