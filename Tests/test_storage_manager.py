"""Юнит-тесты для Src.Logics.storage_manager.StorageManager."""

import json

import pytest

from Src.Core.exception import ValidationException
from Src.Logics.storage_manager import StorageManager
from Src.Models.ingredient_model import IngredientModel
from Src.Models.settings_model import SettingsModel

COLLECTIONS = [
    "measurement_units",
    "nomenclature_groups",
    "nomenclature",
    "restaurants",
    "production_shops",
    "warehouses",
    "technological_maps",
]


def _build_settings(first_start: bool = True) -> SettingsModel:
    """Строит настройки с заданным признаком первого запуска."""
    settings = SettingsModel()
    settings.first_start = first_start
    return settings


def _build_started_manager() -> StorageManager:
    """Возвращает хранилище, запущенное в режиме первого старта."""
    manager = StorageManager()
    manager.start(_build_settings())
    return manager


def _by_name(items: list) -> dict:
    """Возвращает словарь элементов коллекции по имени."""
    return {item.name: item for item in items}


def _ingredients(manager: StorageManager) -> list[IngredientModel]:
    """Возвращает ингредиенты-сырьё всех блюд технологических карт хранилища."""
    return [
        item
        for tmap in manager.technological_maps
        for dish in tmap.dishes
        for item in dish.ingredients
        if isinstance(item, IngredientModel)
    ]


def _same_objects(left: list, right: list) -> bool:
    """Проверяет, что списки состоят из одних и тех же объектов в том же порядке."""
    return len(left) == len(right) and all(
        a is b for a, b in zip(left, right, strict=True)
    )


def test_storage_manager__two_instances__same_object():
    """Повторное создание хранилища возвращает тот же экземпляр (singleton)."""
    # Действие
    first = StorageManager()
    second = StorageManager()

    # Проверки
    assert first is second


def test_storage_manager__start_via_one_instance__data_visible_in_another():
    """Данные, сформированные через один экземпляр, видны через другой."""
    # Подготовка
    manager = _build_started_manager()

    # Действие
    nomenclature = StorageManager().nomenclature

    # Проверки
    assert _same_objects(nomenclature, manager.nomenclature)


def test_storage_manager__constructor__not_loaded_and_empty():
    """До запуска хранилище не загружено, а все коллекции пусты."""
    # Действие
    manager = StorageManager()

    # Проверки
    assert not manager.is_loaded
    assert manager.settings is None
    assert all(getattr(manager, name) == [] for name in COLLECTIONS)


def test_storage_manager__start_first_start__is_loaded_and_settings_kept():
    """При первом старте данные формируются, а настройки сохраняются в хранилище."""
    # Подготовка
    settings = _build_settings(first_start=True)
    manager = StorageManager()

    # Действие
    manager.start(settings)

    # Проверки
    assert manager.is_loaded
    assert manager.settings is settings


def test_storage_manager__start_not_first_start__data_not_formed():
    """При first_start = False данные не формируются и хранилище не загружено."""
    # Подготовка
    manager = StorageManager()

    # Действие
    manager.start(_build_settings(first_start=False))

    # Проверки
    assert not manager.is_loaded
    assert all(getattr(manager, name) == [] for name in COLLECTIONS)


def test_storage_manager__start_twice__data_not_recreated():
    """Повторный запуск не пересоздаёт уже сформированные объекты."""
    # Подготовка
    manager = _build_started_manager()
    nomenclature = manager.nomenclature

    # Действие
    manager.start(_build_settings())

    # Проверки
    assert _same_objects(manager.nomenclature, nomenclature)


def test_storage_manager__start_not_settings_model__raises():
    """Запуск с настройками не типа SettingsModel вызывает исключение валидации."""
    # Подготовка
    manager = StorageManager()

    # Действие и проверки
    with pytest.raises(ValidationException):
        manager.start("настройки")


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__collection_property__returns_copy(collection):
    """Изменение полученного списка не меняет коллекцию хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действие
    getattr(manager, collection).clear()

    # Проверки
    assert getattr(manager, collection) != []


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__first_start__collection_is_filled(collection):
    """При первом старте каждая коллекция хранилища заполнена."""
    # Подготовка
    manager = _build_started_manager()

    # Действие
    items = getattr(manager, collection)

    # Проверки
    assert items != []


@pytest.mark.parametrize(
    ("unit", "base_unit"), [("килограмм", "грамм"), ("литр", "миллилитр")]
)
def test_storage_manager__first_start__derived_unit_refers_to_base_unit(
    unit, base_unit
):
    """Кратная единица ссылается на тот же объект базовой единицы из хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действие
    units = _by_name(manager.measurement_units)

    # Проверки
    assert units[unit].base_unit is units[base_unit]


def test_storage_manager__first_start__nomenclature_refers_to_stored_objects():
    """Группа и единица каждой номенклатуры — объекты из коллекций хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действие
    nomenclature = manager.nomenclature

    # Проверки
    for position in nomenclature:
        assert any(position.group is group for group in manager.nomenclature_groups)
        assert any(
            position.measurement_unit is unit for unit in manager.measurement_units
        )


def test_storage_manager__first_start__warehouse_owners_are_stored_objects():
    """Владелец каждого склада — ресторан или цех из коллекций хранилища."""
    # Подготовка
    manager = _build_started_manager()
    owners = [*manager.restaurants, *manager.production_shops]

    # Действие
    warehouses = manager.warehouses

    # Проверки
    for warehouse in warehouses:
        assert any(warehouse.warehouse_owner is owner for owner in owners)


def test_storage_manager__first_start__all_ids_are_unique():
    """Каждый сформированный объект уникален: идентификаторы не повторяются."""
    # Подготовка
    manager = _build_started_manager()
    objects = [
        *manager.measurement_units,
        *manager.nomenclature_groups,
        *manager.nomenclature,
        *manager.restaurants,
        *manager.production_shops,
        *manager.warehouses,
        *(warehouse.premises for warehouse in manager.warehouses),
        *manager.technological_maps,
        *(dish for tmap in manager.technological_maps for dish in tmap.dishes),
        *_ingredients(manager),
    ]

    # Действие
    ids = [item.id for item in objects]

    # Проверки
    assert len(ids) == len(set(ids))


def test_storage_manager__first_start__ingredients_refer_to_stored_objects():
    """Группа и единица каждого ингредиента — объекты из коллекций хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действие
    ingredients = _ingredients(manager)

    # Проверки
    for ingredient in ingredients:
        assert any(ingredient.group is group for group in manager.nomenclature_groups)
        assert any(
            ingredient.measurement_unit is unit for unit in manager.measurement_units
        )


def test_storage_manager__first_start__recipe_positions_exist():
    """Номенклатура содержит ингредиенты, тесто и блюдо рецепта пиццы Маргарита."""
    # Подготовка
    manager = _build_started_manager()

    # Действие
    names = _by_name(manager.nomenclature).keys()

    # Проверки
    assert {
        "Мука пшеничная",
        "Дрожжи сухие",
        "Соль",
        "Масло оливковое",
        "Сыр Моцарелла",
        "Томаты",
        "Базилик",
        "Тесто для пиццы",
        "Пицца Маргарита",
    } <= names


def test_storage_manager__first_start__technological_map_is_margherita():
    """Хранилище содержит технологическую карту «Пицца Маргарита» с тестом и пиццей."""
    # Подготовка
    manager = _build_started_manager()

    # Действие
    maps = _by_name(manager.technological_maps)

    # Проверки
    assert list(maps) == ["Пицца Маргарита"]
    assert [dish.name for dish in maps["Пицца Маргарита"].dishes] == [
        "Тесто для пиццы",
        "Пицца Маргарита",
    ]


def test_storage_manager__save__all_collections_in_json(tmp_path):
    """Выгрузка пишет в json все справочники, ссылки — вложенными словарями."""
    # Подготовка
    manager = _build_started_manager()
    file_name = tmp_path / "storage.json"

    # Действие
    manager.save(str(file_name))

    # Проверки
    data = json.loads(file_name.read_text(encoding="utf-8"))
    assert set(data) == set(COLLECTIONS)
    units = {unit["name"]: unit for unit in data["measurement_units"]}
    assert units["килограмм"]["base_unit"] == units["грамм"]
