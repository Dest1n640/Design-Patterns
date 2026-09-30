from Src.Core.abstract_model import AbstractModel
from Src.Core.validation import Validation


class NamedModel(AbstractModel):
    """Класс для именнованых сущностей."""

    def __init__(self, name: str) -> None:
        """Конструктор с именем для сущности."""
        super().__init__()
        self.__name = self._validate_name(name)

    @property
    def name(self) -> str:
        """Возвращаем имя сущности."""
        return self.__name

    @name.setter
    def name(self, new_name: str):
        """Устанавливаем имя сущности."""
        self.__name = self._validate_name(new_name)

    def _validate_name(self, value: str) -> str:
        """Проверяет имя и возвращает его без пробелов по краям."""
        return Validation.validate_string(value, "name")
