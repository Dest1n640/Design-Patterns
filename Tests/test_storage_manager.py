"""Юнит-тесты для Src.Logics.storage_manager.StorageManager."""

import json
from pathlib import Path

import pytest

from Src.Core.exception import ValidationException
from Src.Core.position_type import PositionType
from Src.Logics.storage_manager import StorageManager
from Src.Models.settings_model import SettingsModel

# Свойства хранилища, совпадающие по имени с разделами settings.json.
SECTIONS = [
    "measurement_units",
    "nomenclature_groups",
    "nomenclature",
    "restaurants",
    "warehouses",
]
COLLECTIONS = [*SECTIONS, "production_shops"]


def _write_json(directory: Path, data: object) -> str:
    """Записывает данные во временный json-файл и возвращает путь к нему."""
    path = directory / "settings.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _build_settings(first_start: bool = True) -> SettingsModel:
    """Строит настройки с заданным признаком первого запуска."""
    settings = SettingsModel()
    settings.first_start = first_start
    return settings


def _build_started_manager() -> StorageManager:
    """Возвращает хранилище, запущенное в режиме первого старта на settings.json."""
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
    """При первом старте данные загружаются, а настройки сохраняются в хранилище."""
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


@pytest.mark.parametrize("section", SECTIONS)
def test_storage_manager__first_start__names_match_json(settings_data, section):
    """Состав коллекции совпадает с одноимённым разделом settings.json."""
    items = getattr(_build_started_manager(), section)
    assert [item.name for item in items] == [
        item["name"] for item in settings_data[section]
    ]


def test_storage_manager__first_start__production_shop_matches_json(settings_data):
    """Сформирован ровно один производственный цех из раздела production_workshop."""
    shops = _build_started_manager().production_shops
    assert [shop.name for shop in shops] == [
        settings_data["production_workshop"]["name"]
    ]


def test_storage_manager__first_start__base_units_are_shared_objects(settings_data):
    """Базовая единица — тот же объект, что и в коллекции единиц измерения."""
    units = _by_name(_build_started_manager().measurement_units)
    for item in settings_data["measurement_units"]:
        base_unit = units[item["base_unit"]] if item["base_unit"] else None
        assert units[item["name"]].base_unit is base_unit


def test_storage_manager__first_start__nomenclature_matches_json(settings_data):
    """Группа и единица номенклатуры — объекты из коллекций, тип — как в файле."""
    manager = _build_started_manager()
    groups = _by_name(manager.nomenclature_groups)
    units = _by_name(manager.measurement_units)
    nomenclature = _by_name(manager.nomenclature)
    for item in settings_data["nomenclature"]:
        position = nomenclature[item["name"]]
        assert position.full_name == item["full_name"]
        assert position.group is groups[item["group"]]
        assert position.measurement_unit is units[item["measurement_unit"]]
        assert position.position_type is PositionType(item["position_type"])


def test_storage_manager__first_start__warehouse_owners_match_json(settings_data):
    """Центральный склад принадлежит цеху, остальные — ресторанам по коду."""
    manager = _build_started_manager()
    warehouses = _by_name(manager.warehouses)
    restaurants = _by_name(manager.restaurants)
    restaurant_names = {
        item["id"]: item["name"] for item in settings_data["restaurants"]
    }
    for item in settings_data["warehouses"]:
        owner = warehouses[item["name"]].warehouse_owner
        if item["type"] == "central":
            assert owner is manager.production_shops[0]
        else:
            assert owner is restaurants[restaurant_names[item["restaurant_id"]]]


def test_storage_manager__first_start__premises_match_json(settings_data):
    """Помещения складов заполнены данными из settings.json."""
    warehouses = _by_name(_build_started_manager().warehouses)
    for item in settings_data["warehouses"]:
        premises = warehouses[item["name"]].premises
        assert premises.name == item["premises"]["name"]
        assert premises.address == item["premises"]["address"]
        assert premises.square == item["premises"]["square"]


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
    ]
    ids = [item.id for item in objects]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "corrupt",
    [
        pytest.param(
            lambda data: data["measurement_units"].append(
                dict(data["measurement_units"][0])
            ),
            id="duplicate_name",
        ),
        pytest.param(
            lambda data: data["warehouses"][1].update(type="moon"),
            id="unknown_warehouse_type",
        ),
        pytest.param(lambda data: data.pop("nomenclature"), id="missing_section"),
    ],
)
def test_storage_manager__load_invalid_data__raises_validation_exception(
    settings_data, tmp_path, corrupt
):
    """Некорректные данные в файле вызывают исключение валидации."""
    corrupt(settings_data)
    with pytest.raises(ValidationException):
        StorageManager().load(_write_json(tmp_path, settings_data))


def test_storage_manager__load_invalid_after_start__keeps_previous_data(
    settings_data, tmp_path
):
    """Неудачная загрузка не меняет коллекции и признак прошлой загрузки."""
    manager = _build_started_manager()
    nomenclature = manager.nomenclature
    # Ошибка в последнем обрабатываемом разделе: предыдущие уже собраны заново.
    settings_data["warehouses"][1]["restaurant_id"] = "R99"

    with pytest.raises(ValidationException):
        manager.load(_write_json(tmp_path, settings_data))

    assert manager.is_loaded
    assert _same_objects(manager.nomenclature, nomenclature)
