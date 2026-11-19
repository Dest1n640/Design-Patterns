from typing import Self

from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation


class PremisesModel(NamedModel):
    """Класс помещения, в котором расположен склад."""

    def __init__(self) -> None:
        """Инициализирует помещение без заполненных обязательных полей."""
        super().__init__()
        self.__address = ""
        self.__square: int | float | None = None

    @classmethod
    def create(cls, name: str, address: str, square: int | float) -> Self:
        """Создаёт помещение с проверенными адресом и площадью."""
        model = cls()
        model.name = name
        model.address = address
        model.square = square
        model.validate()
        return model

    @property
    def address(self):
        """Возвращает адрес помещения."""
        return self.__address

    @property
    def square(self):
        """Возвращает площадь помещения."""
        return self.__square

    @address.setter
    def address(self, new_address: str):
        """Устанавливает адрес помещения."""
        self.__address = Validation.validate_string(new_address, "address")

    @square.setter
    def square(self, new_square: int | float):
        """Устанавливает площадь помещения."""
        self.__square = Validation.validate_positive_number(new_square, "square")
