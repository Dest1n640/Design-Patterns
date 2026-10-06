"""Юнит-тесты для Src.Logics.storage_manager.StorageManager."""

import pytest

from Src.Core.exception import ValidationException
from Src.Logics.storage_manager import StorageManager
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


def _same_objects(left: list, right: list) -> bool:
    """Проверяет, что списки состоят из одних и тех же объектов в том же порядке."""
    return len(left) == len(right) and all(
        a is b for a, b in zip(left, right, strict=True)
    )


def test_storage_manager__two_instances__same_object():
    """Повторное создание хранилища возвращает тот же экземпляр (singleton)."""
    assert StorageManager() is StorageManager()


def test_storage_manager__start_via_one_instance__data_visible_in_another():
    """Данные, сформированные через один экземпляр, видны через другой."""
    manager = _build_started_manager()
    assert _same_objects(StorageManager().nomenclature, manager.nomenclature)


def test_storage_manager__constructor__not_loaded_and_empty():
    """До запуска хранилище не загружено, а все коллекции пусты."""
    manager = StorageManager()
    assert not manager.is_loaded
    assert manager.settings is None
    assert all(getattr(manager, name) == [] for name in COLLECTIONS)


def test_storage_manager__start_first_start__is_loaded_and_settings_kept():
    """При первом старте данные формируются, а настройки сохраняются в хранилище."""
    settings = _build_settings(first_start=True)
    manager = StorageManager()
    manager.start(settings)
    assert manager.is_loaded
    assert manager.settings is settings


def test_storage_manager__start_not_first_start__data_not_formed():
    """При first_start = False данные не формируются и хранилище не загружено."""
    manager = StorageManager()
    manager.start(_build_settings(first_start=False))
    assert not manager.is_loaded
    assert all(getattr(manager, name) == [] for name in COLLECTIONS)


def test_storage_manager__start_twice__data_not_recreated():
    """Повторный запуск не пересоздаёт уже сформированные объекты."""
    manager = _build_started_manager()
    nomenclature = manager.nomenclature
    manager.start(_build_settings())
    assert _same_objects(manager.nomenclature, nomenclature)


def test_storage_manager__start_not_settings_model__raises():
    """Запуск с настройками не типа SettingsModel вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        StorageManager().start("настройки")


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__collection_property__returns_copy(collection):
    """Изменение полученного списка не меняет коллекцию хранилища."""
    manager = _build_started_manager()
    getattr(manager, collection).clear()
    assert getattr(manager, collection) != []


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__first_start__collection_is_filled(collection):
    """При первом старте каждая коллекция хранилища заполнена."""
    assert getattr(_build_started_manager(), collection) != []


@pytest.mark.parametrize(
    ("unit", "base_unit"), [("килограмм", "грамм"), ("литр", "миллилитр")]
)
def test_storage_manager__first_start__derived_unit_refers_to_base_unit(
    unit, base_unit
):
    """Кратная единица ссылается на тот же объект базовой единицы из хранилища."""
    units = _by_name(_build_started_manager().measurement_units)
    assert units[unit].base_unit is units[base_unit]


def test_storage_manager__first_start__nomenclature_refers_to_stored_objects():
    """Группа и единица каждой номенклатуры — объекты из коллекций хранилища."""
    manager = _build_started_manager()
    for position in manager.nomenclature:
        assert any(position.group is group for group in manager.nomenclature_groups)
        assert any(
            position.measurement_unit is unit for unit in manager.measurement_units
        )


def test_storage_manager__first_start__warehouse_owners_are_stored_objects():
    """Владелец каждого склада — ресторан или цех из коллекций хранилища."""
    manager = _build_started_manager()
    owners = [*manager.restaurants, *manager.production_shops]
    for warehouse in manager.warehouses:
        assert any(warehouse.warehouse_owner is owner for owner in owners)


def test_storage_manager__first_start__all_ids_are_unique():
    """Каждый сформированный объект уникален: идентификаторы не повторяются."""
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
        *(
            ingredient
            for tmap in manager.technological_maps
            for dish in tmap.dishes
            for ingredient in dish.ingredients
        ),
    ]
    ids = [item.id for item in objects]
    assert len(ids) == len(set(ids))


def test_storage_manager__first_start__recipe_positions_exist():
    """Номенклатура содержит ингредиенты, тесто и блюдо рецепта пиццы Маргарита."""
    names = _by_name(_build_started_manager().nomenclature).keys()
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
    maps = _by_name(_build_started_manager().technological_maps)
    assert list(maps) == ["Пицца Маргарита"]
    assert [dish.name for dish in maps["Пицца Маргарита"].dishes] == [
        "Тесто для пиццы",
        "Пицца Маргарита",
    ]
