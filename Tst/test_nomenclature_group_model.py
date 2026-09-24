"""Юнит-тесты для Src.models.nomenclature_group_model.nomenclature_group_model."""
from Src.models.nomenclature_group_model import nomenclature_group_model


def test_ValidGroupCreated_Constructor_NameIsSet():
    """Валидное создание группы номенклатуры сохраняет переданное имя (смоук-тест)."""
    group = nomenclature_group_model("Бакалея")
    assert group.name == "Бакалея"
