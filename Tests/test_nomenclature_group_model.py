"""Юнит-тесты для Src.Models.nomenclature_group_model.NomenclatureGroupModel."""

from Src.Models.nomenclature_group_model import NomenclatureGroupModel


def test_nomenclature_group_model__constructor__name_is_set():
    """Валидное создание группы номенклатуры сохраняет переданное имя (смоук-тест)."""
    group = NomenclatureGroupModel("Бакалея")
    assert group.name == "Бакалея"
