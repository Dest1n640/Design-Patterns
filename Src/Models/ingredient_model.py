from typing import Self

from Src.Core.position_type import PositionType
from Src.Core.validation import Validation
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.nomenclature_model import NomenclatureModel


class IngredientModel(NomenclatureModel):
    """Класс ингредиента — номенклатура с весом брутто и нетто."""

    def __init__(
        self,
        name: str,
        full_name: str,
        group: NomenclatureGroupModel,
        measurement_unit: MeasurementUnitModel,
        position_type: PositionType,
        brutto: int | float,
        netto: int | float,
    ):
        """Конструктор ингредиента."""
        super().__init__(name, full_name, group, measurement_unit, position_type)
        self.brutto = brutto
        self.netto = netto

    @property
    def brutto(self) -> int | float:
        """Возвращает вес ингредиента брутто."""
        return self.__brutto

    @property
    def netto(self) -> int | float:
        """Возвращает вес ингредиента нетто."""
        return self.__netto

    @brutto.setter
    def brutto(self, new_brutto: int | float):
        """Устанавливает вес ингредиента брутто."""
        self.__brutto = Validation.validate_positive_number(new_brutto, "brutto")

    @netto.setter
    def netto(self, new_netto: int | float):
        """Устанавливает вес ингредиента нетто."""
        self.__netto = Validation.validate_positive_number(new_netto, "netto")

    @classmethod
    def create_margherita_ingredients(cls) -> dict[str, list[Self]]:
        """Фабричный метод: создаёт ингредиенты рецепта «Пицца Маргарита».

        Возвращает ингредиенты по названию блюда: «Тесто для пиццы» и
        «Пицца Маргарита» (_docs/recipes/pizza_margherita.md). Воду не включаем:
        по рецепту она не учитывается в номенклатуре. Вес брутто и нетто в рецепте
        не различается, поэтому берём одно количество.
        """
        gram = MeasurementUnitModel.create_gram()
        milliliter = MeasurementUnitModel.create_milliliter()
        pantry = NomenclatureGroupModel("Бакалея")
        dairy = NomenclatureGroupModel("Молочные продукты")
        vegetables = NomenclatureGroupModel("Овощи")
        semi_finished = NomenclatureGroupModel("Полуфабрикаты")
        raw = PositionType.RAW_MATERIAL

        return {
            "Тесто для пиццы": [
                cls(
                    "Мука пшеничная",
                    "Мука пшеничная высшего сорта",
                    pantry,
                    gram,
                    raw,
                    150,
                    150,
                ),
                cls(
                    "Масло оливковое",
                    "Масло оливковое Extra Virgin",
                    pantry,
                    milliliter,
                    raw,
                    5,
                    5,
                ),
                cls("Соль", "Соль поваренная пищевая", pantry, gram, raw, 3, 3),
                cls(
                    "Дрожжи сухие",
                    "Дрожжи хлебопекарные сухие",
                    pantry,
                    gram,
                    raw,
                    2,
                    2,
                ),
            ],
            "Пицца Маргарита": [
                cls(
                    "Тесто для пиццы",
                    "Тесто дрожжевое для пиццы",
                    semi_finished,
                    gram,
                    PositionType.SEMI_FINISHED,
                    250,
                    250,
                ),
                cls("Томаты", "Томаты свежие", vegetables, gram, raw, 150, 150),
                cls(
                    "Сыр Моцарелла",
                    "Сыр Моцарелла для пиццы 45%",
                    dairy,
                    gram,
                    raw,
                    125,
                    125,
                ),
                cls(
                    "Масло оливковое",
                    "Масло оливковое Extra Virgin",
                    pantry,
                    milliliter,
                    raw,
                    10,
                    10,
                ),
                cls("Базилик", "Базилик зелёный свежий", vegetables, gram, raw, 5, 5),
                cls("Соль", "Соль поваренная пищевая", pantry, gram, raw, 1, 1),
            ],
        }
