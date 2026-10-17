from abc import abstractmethod

from Src.Core.abstract_report import AbstractReport
from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel
from Src.Dtos.report_model import ReportModel
from Src.Models.dish_model import DishModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_model import NomenclatureModel
from Src.Models.technological_map_model import TechnologicalMapModel

type Header = tuple[str, ...]
type Row = tuple[object, ...]


class TableReport(AbstractReport):
    """Основа табличных отчётов: строки сущности оформляются в формате наследника."""

    DISH_HEADER = ("Код", "Наименование", "Брутто", "Нетто")
    RECIPE_HEADER = ("Блюдо", *DISH_HEADER)
    NOMENCLATURE_HEADER = (
        "Код",
        "Наименование",
        "Полное наименование",
        "Группа",
        "Единица измерения",
        "Тип",
    )
    UNIT_HEADER = ("Код", "Наименование", "Коэффициент", "Базовая единица")

    def build(self, source: NamedModel) -> ReportModel:
        """Строит отчёт по сущности в формате наследника: текст или байты."""
        header, rows = self._table(source)
        content = self._format(source.name, header, rows)
        if isinstance(content, bytes):
            return ReportModel(source.name, binary=content)
        return ReportModel(source.name, text=content)

    @classmethod
    def _table(cls, source: NamedModel) -> tuple[Header, list[Row]]:
        """Возвращает шапку и строки таблицы для сущности поддерживаемого типа."""
        if isinstance(source, TechnologicalMapModel):
            rows = [(d.name, *row) for d in source.dishes for row in cls._dish_rows(d)]
            return cls.RECIPE_HEADER, rows
        if isinstance(source, DishModel):
            return cls.DISH_HEADER, cls._dish_rows(source)
        if isinstance(source, NomenclatureModel):
            row = (
                source.id,
                source.name,
                source.full_name,
                source.group.name,
                source.measurement_unit.name,
                source.position_type.value,
            )
            return cls.NOMENCLATURE_HEADER, [row]
        if isinstance(source, MeasurementUnitModel):
            base_unit = source.base_unit.name if source.base_unit else ""
            row = (source.id, source.name, source.coefficient, base_unit)
            return cls.UNIT_HEADER, [row]
        raise ValidationException("source", "Отчёт для такого источника не поддержан")

    @staticmethod
    def _dish_rows(dish: DishModel) -> list[Row]:
        """Возвращает строки состава блюда; вес вложенного блюда считается суммарно."""
        rows = []
        for item in dish.ingredients:
            if isinstance(item, DishModel):
                brutto, netto = item.calculate_brutto(), item.calculate_netto()
            else:
                brutto, netto = item.brutto, item.netto
            rows.append((item.id, item.name, brutto, netto))
        return rows

    @abstractmethod
    def _format(self, title: str, header: Header, rows: list[Row]) -> str | bytes:
        """Оформляет шапку и строки таблицы в текст или байты нужного формата."""
