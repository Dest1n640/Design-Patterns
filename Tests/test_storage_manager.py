"""Юнит-тесты для Src.Logics.storage_manager.StorageManager."""

import json

import pytest

from Src.Core.exception import NotFoundException, ValidationException
from Src.Logics.model_registry import ENTITY_TYPES
from Src.Logics.serialize_factory import SerializeFactory
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager
from Src.Models.ingredient_model import IngredientModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
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
ALL_COLLECTIONS = [
    *COLLECTIONS,
    "organizations",
    "premises",
    "dishes",
    "ingredients",
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


def test_storage_manager__get_entity_types_empty_storage__all_collections():
    """Имена коллекций доступны даже в пустом хранилище."""
    # Подготовка
    manager = StorageManager()

    # Действия
    entity_types = manager.get_entity_types()

    # Проверки
    assert set(entity_types) == set(ALL_COLLECTIONS)


def test_storage_manager__registered_model__read_and_save_supported(
    monkeypatch, tmp_path
):
    """Одна регистрация подключает новую модель к чтению, поиску и сохранению."""

    # Подготовка
    class ExtraGroupModel(NomenclatureGroupModel):
        """Дополнительная доменная модель для проверки расширения реестра."""

        def __init__(self, name: str, unit: MeasurementUnitModel) -> None:
            """Создаёт группу со вложенной единицей измерения."""
            super().__init__(name)
            self.__unit = unit

        @property
        def unit(self) -> MeasurementUnitModel:
            """Возвращает единицу измерения группы."""
            return self.__unit

    monkeypatch.setitem(ENTITY_TYPES, "extra_groups", ExtraGroupModel)
    manager = StorageManager()
    unit = MeasurementUnitModel.create_gram()
    data = {
        "extra_groups": [
            {
                "type": "ExtraGroupModel",
                "id": "extra-group",
                "name": "Группа",
                "unit": SerializeFactory().convert(unit),
            }
        ]
    }
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    manager.read(str(file_name))
    entities = manager.get_entities("extra_groups")
    entity = manager.get_entity("extra_groups", "extra-group")
    manager.save(str(file_name))
    saved = json.loads(file_name.read_text(encoding="utf-8"))

    # Проверки
    assert "extra_groups" in manager.get_entity_types()
    assert type(entity) is ExtraGroupModel
    assert entity is entities[0]
    assert entity.unit is manager.get_entity("measurement_units", unit.id)
    assert saved["extra_groups"] == data["extra_groups"]


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__get_entities__stored_objects_returned(collection):
    """Общий метод возвращает объекты любой коллекции хранилища."""
    # Подготовка
    manager = _build_started_manager()
    expected = getattr(manager, collection)

    # Действия
    entities = manager.get_entities(collection)

    # Проверки
    assert _same_objects(entities, expected)


@pytest.mark.parametrize("collection", ["missing", "settings", "_data", "save"])
def test_storage_manager__get_entities_invalid_collection__raises(collection):
    """Неизвестные имена, настройки, закрытые поля и методы недоступны."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    with pytest.raises(NotFoundException) as exc_info:
        manager.get_entities(collection)

    # Проверки
    assert collection in exc_info.value.message


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__get_entity_existing_id__stored_object_returned(collection):
    """Поиск по идентификатору возвращает исходный объект любой коллекции."""
    # Подготовка
    manager = _build_started_manager()
    expected = getattr(manager, collection)[0]

    # Действия
    entity = manager.get_entity(collection, expected.id)

    # Проверки
    assert entity is expected


def test_storage_manager__get_entity_missing_id__raises():
    """Поиск отсутствующего идентификатора завершается ошибкой отсутствия сущности."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    with pytest.raises(NotFoundException) as exc_info:
        manager.get_entity("nomenclature_groups", "missing")

    # Проверки
    assert "missing" in exc_info.value.message


def test_storage_manager__renamed_entity__lookup_uses_id():
    """Изменение названия не влияет на поиск объекта по идентификатору."""
    # Подготовка
    manager = _build_started_manager()
    original = manager.nomenclature_groups[0]
    entity_id = original.id

    # Действия
    original.name = "Новое название"
    entity = manager.get_entity("nomenclature_groups", entity_id)

    # Проверки
    assert entity is original
    assert entity.name == "Новое название"


def test_storage_manager__duplicate_names__distinct_ids_preserved(tmp_path):
    """Объекты с одинаковыми названиями сохраняются и находятся по разным id."""
    # Подготовка
    manager = StorageManager()
    data = {
        "nomenclature_groups": [
            {"type": "NomenclatureGroupModel", "id": "first", "name": "Группа"},
            {"type": "NomenclatureGroupModel", "id": "second", "name": "Группа"},
        ]
    }
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    manager.read(str(file_name))
    first = manager.get_entity("nomenclature_groups", "first")
    second = manager.get_entity("nomenclature_groups", "second")
    manager.save(str(file_name))
    saved = json.loads(file_name.read_text(encoding="utf-8"))

    # Проверки
    assert first is not second
    assert first.name == second.name == "Группа"
    assert saved["nomenclature_groups"] == data["nomenclature_groups"]


def test_storage_manager__duplicate_id_across_collections__state_kept(tmp_path):
    """Одинаковые коды в разных коллекциях отклоняются до замены данных."""
    # Подготовка
    manager = _build_started_manager()
    original = manager.nomenclature_groups[0]
    data = {
        "nomenclature_groups": [
            {"type": "NomenclatureGroupModel", "id": "same", "name": "Группа"}
        ],
        "restaurants": [{"type": "RestaurantModel", "id": "same", "name": "Ресторан"}],
    }
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.read(str(file_name))

    # Проверки
    assert exc_info.value.field == "id"
    assert manager.get_entity("nomenclature_groups", original.id) is original


def test_storage_manager__first_start__nested_models_have_collections():
    """Организация и вложенные модели доступны через общие методы хранилища."""
    # Подготовка
    settings_manager = SettingsManager()
    settings_manager.read()
    manager = StorageManager()

    # Действия
    manager.start(settings_manager.settings)
    sources = {
        "organizations": [settings_manager.settings.organization],
        "premises": [warehouse.premises for warehouse in manager.warehouses],
        "dishes": [dish for tmap in manager.technological_maps for dish in tmap.dishes],
        "ingredients": _ingredients(manager),
    }

    # Проверки
    for collection, expected in sources.items():
        assert _same_objects(manager.get_entities(collection), expected)
        for entity in expected:
            assert manager.get_entity(collection, entity.id) is entity


def test_storage_manager__two_instances__same_object():
    """Повторное создание хранилища возвращает тот же экземпляр (singleton)."""
    # Подготовка
    first = StorageManager()

    # Действия
    second = StorageManager()

    # Проверки
    assert first is second


def test_storage_manager__start_via_one_instance__data_visible_in_another():
    """Данные, сформированные через один экземпляр, видны через другой."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    nomenclature = StorageManager().nomenclature

    # Проверки
    assert _same_objects(nomenclature, manager.nomenclature)


def test_storage_manager__constructor__not_loaded_and_empty():
    """До запуска хранилище не загружено, а все коллекции пусты."""
    # Подготовка
    # Дополнительная подготовка не требуется.

    # Действия
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

    # Действия
    manager.start(settings)

    # Проверки
    assert manager.is_loaded
    assert manager.settings is settings


def test_storage_manager__start_not_first_start__data_not_formed():
    """При first_start = False данные не формируются и хранилище не загружено."""
    # Подготовка
    manager = StorageManager()
    settings = _build_settings(first_start=False)

    # Действия
    manager.start(settings)

    # Проверки
    assert not manager.is_loaded
    assert all(getattr(manager, name) == [] for name in COLLECTIONS)


def test_storage_manager__start_twice__data_not_recreated():
    """Повторный запуск не пересоздаёт уже сформированные объекты."""
    # Подготовка
    manager = _build_started_manager()
    nomenclature = manager.nomenclature
    settings = _build_settings()

    # Действия
    manager.start(settings)

    # Проверки
    assert _same_objects(manager.nomenclature, nomenclature)


def test_storage_manager__start_not_settings_model__raises():
    """Запуск с настройками не типа SettingsModel вызывает исключение валидации."""
    # Подготовка
    manager = StorageManager()

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.start("настройки")

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__collection_property__returns_copy(collection):
    """Изменение полученного списка не меняет коллекцию хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    getattr(manager, collection).clear()

    # Проверки
    assert getattr(manager, collection) != []


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__first_start__collection_is_filled(collection):
    """При первом старте каждая коллекция хранилища заполнена."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
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

    # Действия
    units = _by_name(manager.measurement_units)

    # Проверки
    assert units[unit].base_unit is units[base_unit]


def test_storage_manager__first_start__nomenclature_refers_to_stored_objects():
    """Группа и единица каждой номенклатуры — объекты из коллекций хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
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

    # Действия
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

    # Действия
    ids = [item.id for item in objects]

    # Проверки
    assert len(ids) == len(set(ids))


def test_storage_manager__first_start__ingredients_refer_to_stored_objects():
    """Группа и единица каждого ингредиента — объекты из коллекций хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
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

    # Действия
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

    # Действия
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

    # Действия
    manager.save(str(file_name))
    data = json.loads(file_name.read_text(encoding="utf-8"))

    # Проверки
    assert set(data) == set(ALL_COLLECTIONS)
    units = {unit["name"]: unit for unit in data["measurement_units"]}
    assert units["килограмм"]["base_unit"] == units["грамм"]


def test_storage_manager__read_empty_collections__loaded_and_empty(tmp_path):
    """Пустые коллекции загружаются без создания первичных данных."""
    # Подготовка
    manager = _build_started_manager()
    settings = manager.settings
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(dict.fromkeys(COLLECTIONS, [])), encoding="utf-8")

    # Действия
    manager.read(str(file_name))

    # Проверки
    assert manager.is_loaded
    assert manager.settings is settings
    assert all(manager.get_entities(field) == [] for field in ALL_COLLECTIONS)


@pytest.mark.parametrize("data", [None, [], {}])
def test_storage_manager__read_invalid_root__state_kept(tmp_path, data):
    """Неверный корень JSON не заменяет уже сформированные справочники."""
    # Подготовка
    manager = _build_started_manager()
    originals = {field: getattr(manager, field) for field in COLLECTIONS}
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    with pytest.raises(ValidationException):
        manager.read(str(file_name))

    # Проверки
    assert manager.is_loaded
    for field, models in originals.items():
        assert _same_objects(getattr(manager, field), models)


@pytest.mark.parametrize(
    "collection",
    [
        None,
        {},
        [{"type": "MeasurementUnitModel", "name": "грамм", "coefficient": 1}],
        [{"type": "TechnologicalMapModel", "name": "Карта", "id": "same-id"}] * 2,
        [{"type": "UnknownModel"}],
    ],
)
def test_storage_manager__read_invalid_collection__state_kept(tmp_path, collection):
    """Ошибка в последней коллекции не приводит к частичному обновлению хранилища."""
    # Подготовка
    manager = _build_started_manager()
    originals = {field: getattr(manager, field) for field in COLLECTIONS}
    file_name = tmp_path / "storage.json"
    manager.save(str(file_name))
    data = json.loads(file_name.read_text(encoding="utf-8"))
    data["measurement_units"][0]["name"] = "Новое имя из файла"
    data["technological_maps"] = collection
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    with pytest.raises(ValidationException):
        manager.read(str(file_name))

    # Проверки
    assert manager.is_loaded
    for field, models in originals.items():
        assert _same_objects(getattr(manager, field), models)
