"""Проверки однозначного выбора доменных моделей при десериализации."""

from Src.Logics.entity_type import EntityType


def test_entity_type__model_names__unique_for_deserialization():
    """Имена доменных классов однозначно определяют тип модели в JSON."""
    # Подготовка
    # Данные предоставлены перечислением типов сущностей.
    model_types = [entity_type.value for entity_type in EntityType]

    # Действия
    model_names = {model_type.__name__ for model_type in model_types}

    # Проверки
    assert len(model_names) == len(model_types)
