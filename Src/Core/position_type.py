from enum import Enum


class PositionType(Enum):
    """Тип позиции номенклатуры."""

    RAW_MATERIAL = "raw_material"  # сырьё
    GOODS = "goods"  # товар
    SEMI_FINISHED = "semi_finished"  # полуфабрикат
    DISH = "dish"  # блюдо
