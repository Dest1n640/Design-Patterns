from typing import Self

from Src.Core.abstract_manager import AbstractManager
from Src.Models.storage_model import StorageModel
from Src.Core.validation import Validation


class StorageManager(AbstractManager):
    """Класс менеджера складов — singleton, загружает данные хранилища."""

    _instance = None

    def __new__(cls) -> Self:
        """Возвращает единственный экземпляр менеджера складов."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Конструктор: состояние создаётся один раз для единственного экземпляра."""
        if hasattr(self, "_storage"):
            return
        super().__init__()
        self._storage = StorageModel()

    @property
    def storage(self) -> StorageModel:
        """Возвращает модель хранилища."""
        return self._storage

    def convert(self) -> bool:
        """Преобразует загруженные данные в модель хранилища (пока не реализовано)."""
        data = Validation.validate_instance(
            self._data, dict, "storage", "Настройки должны быть json-объектом"
        )

        
