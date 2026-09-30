from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation


class PremisesModel(NamedModel):
    """Класс помещения, в котором расположен склад."""

    def __init__(self, name: str, address: str, square: int | float):
        """Конструктор помещения."""
        super().__init__(name)
        self.address = address
        self.square = square

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
